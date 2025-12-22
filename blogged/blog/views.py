import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from image_processing.meta_data_processing import get_gps_coordinates_from_meta_data
from django.core.exceptions import BadRequest
from django.contrib.auth.decorators import login_required
from dal import autocomplete
from django.utils.html import format_html

from blog.forms import GpsCoordinates, GpsFormSet, ImageFormSet, PostForm
from blog.models import Images, Post, Activity, Organisation


def index(request):
    posts = Post.objects.all()
    return render(request, "index.html", {"posts": posts})


def detail(request, slug, id):
    post = get_object_or_404(Post, slug=slug, id=id)
    post_images = Images.objects.all().filter(post=post)

    return render(
        request,
        "blog/detail.html",
        {
            "post": post,
            "post_images": post_images,
        },
    )


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
