import json

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
from blog.forms import PostForm
from blog.models import Images, Videos
from blog.models import Organisation
from blog.models import Post
from dal import autocomplete
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import BadRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.html import format_html
from hitcount.views import track_hit_count
from image_processing.meta_data_processing import get_gps_coordinates_from_meta_data

SELECT_ALL_OPTION_STR = "-- All --"
SELECT_ALL_OPTION_VAL = "All"


@track_hit_count
def blog_listing(request):
    posts = Post.objects.all()
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
def upload_post(request):
    if request.method == "POST":
        post_form = PostForm(request.POST)
        gps_formset = GpsFormSet(
            request.POST, prefix="gps"
        )  # TODO - "gps-form" would be a better prefix
        image_formset = ImageFormSet(request.POST, request.FILES, prefix="images")

        if post_form.is_valid() and gps_formset.is_valid() and image_formset.is_valid():
            try:
                post = post_form.save()
                gps_formset.instance = post
                gps_formset.save()
                image_formset.instance = post
                image_formset.save()
                messages.info(request, "Post succesfully added")
                print(request, "Post succesfully added")
            except Exception as e:
                # TODO - remove any partially saved data? e.g. if form saving gps_formset fails after post is saved
                messages.error(request, f"Error saving post: {e}")
                print(request, f"Error saving post: {e}")
                raise BadRequest(f"Error saving post: {e}")

        else:
            if not post_form.is_valid():
                messages.error(request, f"Post form errors: {post_form.errors}")
                print(request, f"Post form errors: {post_form.errors}")
            if not gps_formset.is_valid():
                messages.error(request, f"GPS form errors: {gps_formset.errors}")
                print(request, f"GPS form errors: {gps_formset.errors}")
            if not image_formset.is_valid():
                messages.error(request, f"Image form errors: {image_formset.errors}")
                print(request, f"Image form errors: {image_formset.errors}")

        return redirect("upload-post")  # TODO - redirect to the new post detail page

    post_form = PostForm()
    gps_formset = GpsFormSet(queryset=GpsCoordinates.objects.none(), prefix="gps")
    image_formset = ImageFormSet(queryset=Images.objects.none(), prefix="images")

    return render(
        request,
        "blog/upload-post.html",
        {
            "post_form": post_form,
            "image_formset": image_formset,
            "gps_formset": gps_formset,
        },
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
            lat, lon, alt = get_gps_coordinates_from_meta_data(image_path=im.file.name)
            gps_data["gps_array"].append({"lat": lat, "lon": lon, "alt": alt})
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
