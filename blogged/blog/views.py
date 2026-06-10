import json
from pathlib import Path

from activities.models import TransportCar
from activities.models import TransportPublic
from activities.models import TransportWalking
from activities.models import Activity, ActivityTreeGuardRemoval
from activities.models import ActivityInvasiveSpeciesRemoval
from activities.models import ActivitySurveying
from activities.models import ActivityTraining
from activities.models import ActivityTreePlantingSession
from activities.models import ActivityVoleGuardRemoval
from activities.models import ActivityWorkshop
from activities.models import Location
from blog.forms import GpsCoordinates
from blog.forms import GpsFormSet
from blog.forms import ImageFormSet
from blog.forms import VideoFormSet
from blog.forms import PostForm
from blog.forms import PostContentForm
from blog.forms import PostTransportForm
from blog.forms import PostStageOneForm
from blog.models import Images, Videos
from blog.models import Organisation
from blog.models import Post
from dal import autocomplete
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.html import format_html
from django.db import transaction
from hitcount.views import track_hit_count
from image_processing.meta_data_processing import get_gps_coordinates_from_meta_data
from django.urls import reverse

SELECT_ALL_OPTION_STR = "-- All --"
SELECT_ALL_OPTION_VAL = "All"


@track_hit_count
def blog_listing(request):
    posts = Post.objects.filter(status=Post.ArticleStatus.PUBLISHED)
    organisation_tags = Organisation.objects.all()
    activity_tags = {c[0]: c[1] for c in Activity.ActivityType.choices}
    activity_tags[0] = (
        SELECT_ALL_OPTION_STR  # Replace UNDEFINED with SELECT_ALL_OPTION_STR for ui display purposes
    )
    location_tags = Location.choices
    current_activity_id = 0
    current_organisation_id = 0
    current_location_id = SELECT_ALL_OPTION_VAL

    if request.GET.get("activity-select"):
        activity_id = request.GET.get("activity-select")
        current_activity_id = int(activity_id)

        # TODO - ideally the commented line below would work, but it doesn't seem to filter correctly with polymorphic models
        # candidates = Activity.objects.all().filter(activity_type=activity_id)
        # for now we use if/else statements to check each child activity type individually
        if activity_id == SELECT_ALL_OPTION_STR or Activity.ActivityType.GENERIC:
            candidates = Activity.objects.all()
        elif activity_id == str(Activity.ActivityType.TREE_PLANTING_SESSION):
            candidates = ActivityTreePlantingSession.objects.all()
        elif activity_id == str(Activity.ActivityType.VOLE_GUARD_REMOVAL):
            candidates = ActivityVoleGuardRemoval.objects.all()
        elif activity_id == str(Activity.ActivityType.INVASIVE_SPECIES_REMOVAL):
            candidates = ActivityInvasiveSpeciesRemoval.objects.all()
        elif activity_id == str(Activity.ActivityType.TRAINING):
            candidates = ActivityTraining.objects.all()
        elif activity_id == str(Activity.ActivityType.WORKSHOP):
            candidates = ActivityWorkshop.objects.all()
        elif activity_id == str(Activity.ActivityType.SURVEY):
            candidates = ActivitySurveying.objects.all()
        elif activity_id == str(Activity.ActivityType.TREE_GUARD_REMOVAL):
            candidates = ActivityTreeGuardRemoval.objects.all()
        else:
            candidates = Activity.objects.all()

        # select posts that are linked to the filtered activities
        post_ids = [a.post.pk for a in candidates if a.post is not None]
        posts = posts.filter(pk__in=post_ids)

    if request.GET.get("org-select"):
        org_id = request.GET.get("org-select")
        # NOTE: we check isdigit() to avoid filtering when the value is SELECT_ALL_OPTION_STR
        if org_id.isdigit():
            posts = posts.filter(organisation_tags=org_id)
            current_organisation_id = int(org_id)

    if request.GET.get("location-select"):
        location = request.GET.get("location-select")
        # print(f"Filtering by location: {location}")
        if location != SELECT_ALL_OPTION_VAL:
            current_location_id = location
            posts = posts.filter(activities__location=location).distinct()

    return render(
        request,
        "index.html",
        {
            "posts": posts,
            "organisation_tags": organisation_tags,
            "activity_tags": activity_tags,
            "current_activity_id": current_activity_id,
            "current_organisation_id": current_organisation_id,
            "select_all_option_str": SELECT_ALL_OPTION_STR,
            "select_all_option_val": SELECT_ALL_OPTION_VAL,
            "current_location_id": current_location_id,
            "location_select_options": location_tags,
        },
    )


@track_hit_count
def detail(request, slug, id):
    post = get_object_or_404(Post, slug=slug, id=id)
    if post.status != Post.ArticleStatus.PUBLISHED:
        raise Http404("Draft posts are not publicly visible.")

    post_images = Images.objects.all().filter(post=post)
    post_videos = Videos.objects.all().filter(post=post)
    all_media = list(post_images) + list(post_videos)
    captions = [img.caption for img in post_images]
    attributions = ["Jan Stankiewicz" for _ in post_images]

    return render(
        request,
        "blog/detail.html",
        {
            "post": post,
            "all_media": all_media,
            "post_images": post_images,
            "post_videos": post_videos,
            "captions": captions,
            "attributions": attributions,
        },
    )


@track_hit_count
def blog_image_gallery(request):
    images = Images.objects.all()
    print(f"Number of images: {len(images)}")
    return render(request, "blog/blog-image-gallery.html", {"images": images})


class OrganisationAutocomplete(autocomplete.Select2QuerySetView):
    def get_result_label(self, result):
        return format_html('<span style="font-weight: bold;">{}</span>', result.name)

    def get_selected_result_label(self, item):
        return item.name

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Organisation.objects.none()

        qs = Organisation.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class ActivityAutocomplete(autocomplete.Select2QuerySetView):
    def get_result_label(self, result):
        return format_html('<span style="font-weight: bold;">{}</span>', result.name)

    def get_selected_result_label(self, item):
        return item.name

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Activity.objects.none()

        qs = Activity.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


@login_required
def draft_posts(request):
    drafts = []
    for draft in Post.objects.filter(status=Post.ArticleStatus.DRAFT):
        drafts.append(
            {
                "post": draft,
                "resume_stage": "3" if draft.content.strip() else "2",
                "can_publish": bool(draft.content.strip()),
            }
        )

    return render(request, "blog/draft_posts.html", {"drafts": drafts})


@login_required
def publish_post(request, id):
    if request.method != "POST":
        return redirect("draft_posts")

    post = get_object_or_404(Post, id=id, status=Post.ArticleStatus.DRAFT)
    if not post.title or not post.date or not post.content.strip():
        messages.error(request, "Complete the post content before publishing.")
        stage = "1" if (not post.title or not post.date) else ("2" if not post.content.strip() else "3")
        return redirect(f"{reverse('upload-post')}?draft={post.pk}&stage={stage}")

    post.status = Post.ArticleStatus.PUBLISHED
    post.save(update_fields=["status"])
    messages.success(request, "Post published.")
    return redirect(post.get_absolute_url())


@login_required
def delete_draft(request, id):
    if request.method != "POST":
        return redirect("draft_posts")

    post = get_object_or_404(Post, id=id, status=Post.ArticleStatus.DRAFT)
    with transaction.atomic():
        Activity.objects.filter(post=post).delete()
        post.delete()
    return redirect("draft_posts")


@login_required
def upload_post(request):
    draft_id = request.POST.get("draft_id") or request.GET.get("draft")
    draft_post = (
        get_object_or_404(Post, pk=draft_id, status=Post.ArticleStatus.DRAFT)
        if draft_id
        else None
    )
    active_stage = (
        request.POST.get("stage")
        or request.POST.get("publish_stage")
        or request.GET.get("stage")
        or "1"
    )

    def upload_url(post_id: int | None = None, stage: str | None = None) -> str:
        url = reverse("upload-post")
        query_string = []
        if post_id is not None:
            query_string.append(f"draft={post_id}")
        if stage is not None:
            query_string.append(f"stage={stage}")
        return f"{url}?{'&'.join(query_string)}" if query_string else url

    def build_context(
        *,
        active_stage_value: str | None = None,
        stage_one_form=None,
        stage_two_form=None,
        stage_two_transport_form=None,
        gps_formset=None,
        image_formset=None,
        video_formset=None,
        stage_message: str | None = None,
    ):
        transport_initial = {}
        if draft_post:
            car_transport = TransportCar.objects.filter(
                activity__post=draft_post
            ).first()
            public_transport = TransportPublic.objects.filter(
                activity__post=draft_post
            ).first()
            walking_transport = TransportWalking.objects.filter(
                activity__post=draft_post
            ).first()

            if car_transport:
                transport_initial = {
                    "travel_option": PostTransportForm.TRAVEL_OPTION_CAR,
                    "distance": car_transport.distance,
                    "carbon_offset": car_transport.carbon_offset,
                    "powertrain": car_transport.powertrain,
                    "passengers": car_transport.passengers,
                }
            elif public_transport:
                transport_initial = {
                    "travel_option": PostTransportForm.TRAVEL_OPTION_PUBLIC,
                    "distance": public_transport.distance,
                    "carbon_offset": public_transport.carbon_offset,
                    "public_type": public_transport.type,
                }
            elif walking_transport:
                transport_initial = {
                    "travel_option": PostTransportForm.TRAVEL_OPTION_WALKING,
                    "distance": walking_transport.distance,
                    "carbon_offset": walking_transport.carbon_offset,
                }

        context = {
            "draft_post": draft_post,
            "active_stage": active_stage_value or active_stage,
            "stage_one_form": stage_one_form or PostStageOneForm(instance=draft_post),
            "stage_two_form": stage_two_form or PostContentForm(instance=draft_post),
            "stage_two_transport_form": stage_two_transport_form
            or PostTransportForm(initial=transport_initial),
            "gps_formset": gps_formset
            or GpsFormSet(
                queryset=GpsCoordinates.objects.filter(post=draft_post)
                if draft_post
                else GpsCoordinates.objects.none(),
                prefix="gps",
                instance=draft_post,
            ),
            "image_formset": image_formset
            or ImageFormSet(
                queryset=Images.objects.filter(post=draft_post)
                if draft_post
                else Images.objects.none(),
                prefix="images",
                instance=draft_post,
            ),
            "video_formset": video_formset
            or VideoFormSet(
                queryset=Videos.objects.filter(post=draft_post)
                if draft_post
                else Videos.objects.none(),
                prefix="videos",
                instance=draft_post,
            ),
        }

        if stage_message is not None:
            context["stage_message"] = stage_message

        return context

    if request.method == "POST" and active_stage == "1":
        stage_one_form = PostStageOneForm(request.POST, instance=draft_post)
        if stage_one_form.is_valid():
            post = stage_one_form.save(commit=False)
            post.status = Post.ArticleStatus.DRAFT
            post.save()
            stage_one_form.save_m2m()
            messages.success(request, "Stage 1 saved. Continue with the content step.")
            return redirect(upload_url(post.pk, "2"))

        return render(
            request,
            "blog/upload-post.html",
            build_context(stage_one_form=stage_one_form, active_stage_value="1"),
        )

    if request.method == "POST" and active_stage == "2":
        if draft_post is None:
            messages.error(request, "Save stage 1 first before entering content.")
            return redirect(upload_url(stage="1"))

        stage_two_form = PostContentForm(request.POST, instance=draft_post)
        stage_two_transport_form = PostTransportForm(request.POST)
        if stage_two_form.is_valid() and stage_two_transport_form.is_valid():
            stage_two_form.save()

            selected_activity = Activity.objects.filter(post=draft_post).first()
            if selected_activity is None:
                selected_activity = Activity.objects.create(post=draft_post)

            TransportCar.objects.filter(activity__post=draft_post).delete()
            TransportPublic.objects.filter(activity__post=draft_post).delete()
            TransportWalking.objects.filter(activity__post=draft_post).delete()

            travel_option = stage_two_transport_form.cleaned_data.get("travel_option")
            if travel_option:
                transport_kwargs = {
                    "activity": selected_activity,
                    "distance": stage_two_transport_form.cleaned_data.get("distance"),
                    "carbon_offset": stage_two_transport_form.cleaned_data.get(
                        "carbon_offset"
                    ),
                }

                if travel_option == PostTransportForm.TRAVEL_OPTION_CAR:
                    TransportCar.objects.create(
                        **transport_kwargs,
                        powertrain=stage_two_transport_form.cleaned_data.get(
                            "powertrain"
                        ),
                        passengers=stage_two_transport_form.cleaned_data.get(
                            "passengers"
                        ),
                    )
                elif travel_option == PostTransportForm.TRAVEL_OPTION_PUBLIC:
                    TransportPublic.objects.create(
                        **transport_kwargs,
                        type=stage_two_transport_form.cleaned_data.get("public_type"),
                    )
                elif travel_option == PostTransportForm.TRAVEL_OPTION_WALKING:
                    TransportWalking.objects.create(**transport_kwargs)

            messages.success(request, "Stage 2 saved. Add photos and GPS data next.")
            return redirect(upload_url(draft_post.pk, "3"))

        return render(
            request,
            "blog/upload-post.html",
            build_context(
                stage_two_form=stage_two_form,
                stage_two_transport_form=stage_two_transport_form,
                active_stage_value="2",
            ),
        )

    if request.method == "POST" and active_stage == "3":
        if draft_post is None:
            messages.error(
                request, "Save stage 1 first before adding media or GPS data."
            )
            return redirect(upload_url(stage="1"))

        publish_after_save = request.POST.get("action") == "publish"

        post_data = request.POST.copy()
        # Backward compatibility for requests/tests that predate video management fields.
        if "videos-TOTAL_FORMS" not in post_data:
            post_data.update(
                {
                    "videos-TOTAL_FORMS": "0",
                    "videos-INITIAL_FORMS": "0",
                    "videos-MIN_NUM_FORMS": "0",
                    "videos-MAX_NUM_FORMS": "1000",
                }
            )

        gps_formset = GpsFormSet(post_data, prefix="gps", instance=draft_post)
        image_formset = ImageFormSet(
            post_data,
            request.FILES,
            prefix="images",
            instance=draft_post,
        )
        video_formset = VideoFormSet(
            post_data,
            request.FILES,
            prefix="videos",
            instance=draft_post,
        )

        if (
            gps_formset.is_valid()
            and image_formset.is_valid()
            and video_formset.is_valid()
        ):
            with transaction.atomic():
                gps_formset.save()
                image_formset.save()
                video_formset.save()

                if publish_after_save:
                    if not draft_post.content.strip():
                        messages.error(
                            request, "Complete the content step before publishing."
                        )
                        return redirect(upload_url(draft_post.pk, "2"))

                    draft_post.status = Post.ArticleStatus.PUBLISHED
                    draft_post.save(update_fields=["status"])
                    messages.success(request, "Post published.")
                    return redirect(draft_post.get_absolute_url())

            messages.success(request, "Stage 3 saved. Your draft is ready for review.")
            return redirect(upload_url(draft_post.pk, "3"))

        return render(
            request,
            "blog/upload-post.html",
            build_context(
                gps_formset=gps_formset,
                image_formset=image_formset,
                video_formset=video_formset,
                active_stage_value="3",
            ),
        )

    if request.method == "POST":
        post_form = PostForm(request.POST, instance=draft_post)
        gps_formset = GpsFormSet(
            request.POST,
            prefix="gps",
            instance=draft_post,
        )
        image_formset = ImageFormSet(
            request.POST,
            request.FILES,
            prefix="images",
            instance=draft_post,
        )

        if post_form.is_valid() and gps_formset.is_valid() and image_formset.is_valid():
            with transaction.atomic():
                post = post_form.save(commit=False)
                post.status = Post.ArticleStatus.DRAFT
                post.save()
                post_form.save_m2m()
                gps_formset.instance = post
                gps_formset.save()
                image_formset.instance = post
                image_formset.save()

            messages.success(request, "Post successfully saved.")
        else:
            if not post_form.is_valid():
                messages.error(request, f"Post form errors: {post_form.errors}")
            if not gps_formset.is_valid():
                messages.error(request, f"GPS form errors: {gps_formset.errors}")
            if not image_formset.is_valid():
                messages.error(request, f"Image form errors: {image_formset.errors}")

        return redirect("upload-post")

    return render(
        request,
        "blog/upload-post.html",
        build_context(active_stage_value=active_stage),
    )


def upload_image(request):
    if request.method == "POST":
        pass

    return render(request, "blog/partials/image.html")


def upload_location(request):
    if request.method == "POST":
        pass
    return render(request, "blog/partials/location_upload.html")


def handle_extract_gps_coords(request):
    gps_data = {"gps_data_found": True, "gps_array": []}
    for im in request.FILES.values():
        try:
            image_path = getattr(im.file, "name", None) or im.file
            lat, lon, alt = get_gps_coordinates_from_meta_data(image_path=image_path)
            source_name = Path(getattr(im, "name", "")).name
            gps_data["gps_array"].append(
                {
                    "lat": float(lat),
                    "lon": float(lon),
                    "alt": float(alt),
                    "source_name": source_name,
                }
            )
        except LookupError:
            gps_data["gps_data_found"] = False
            # TODO - display this in the app
            print(
                f"skipping image {im.file.name} since it doesn't have the required GPS meta data"
            )

    json_response = JsonResponse(
        json.dumps(gps_data), safe=False
    )  # TODO - is it OK to have safe=False?

    return json_response
