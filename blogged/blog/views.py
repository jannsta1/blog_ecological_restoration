import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse

from .models import Images, Post, MediaAttachment
from .forms import ImageFormSet, GpsFormSet, GpsCoordinates, Images, CommentForm, PostForm
from image_processing.meta_data_processing import get_gps_coordinates_from_meta_data



def index(request):
    posts = Post.objects.all()
    return render(request, 'index.html', {'posts': posts})

def detail(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()

            return redirect('detail', slug=slug)
    else:
        
        form = CommentForm()
        post_images = Images.objects.all().filter(post=post)

    return render(request, 'blog/detail.html', 
                  {'post': post,
                    'form': form,
                    'post_images': post_images,
                   })

def blog_image_gallery(request):

    images = MediaAttachment.objects.all()
    return render(request, 'blog/blog-image-gallery.html', {'images': images})




# TODO # @login_required
def upload_post(request):

    if request.method == 'POST':

        post_form = PostForm(request.POST)
        gps_formset = GpsFormSet(request.POST, prefix="gps")  # TODO - "gps-form" would be a better prefix
        image_formset = ImageFormSet(request.POST, request.FILES, prefix="images")

        if post_form.is_valid() and gps_formset.is_valid() and image_formset.is_valid():
            post = post_form.save()
            gps_formset.instance = post
            gps_formset.save()
            image_formset.instance = post
            image_formset.save()
            messages.success(request, "Post succesfully added")

        else:
            if not post_form.is_valid():
                print("Error in post form!")
                print(post_form.errors)
            if not gps_formset.is_valid():
                print(gps_formset.errors)
                print("Error in GPS form!")
            if not image_formset.is_valid():
                print("Error in Image form!")
                print(image_formset.errors)        

        return redirect('index')
    
    post_form = PostForm()
    gps_formset = GpsFormSet(queryset=GpsCoordinates.objects.none(), prefix="gps")
    image_formset = ImageFormSet(queryset=Images.objects.none(), prefix="images")

    return render(request, 'blog/upload-post.html',
                {'post_form': post_form, 'image_formset': image_formset, 'gps_formset': gps_formset})


def upload_image(request):

    if request.method == "POST":
        pass

    return render(request, 'blog/partials/image.html')

def upload_location(request):

    if request.method == "POST":
        pass
    return render(request, 'blog/partials/location_upload.html')


def handle_extract_gps_coords(request):

    gps_data = {"gps_data_found": True, "gps_array": []}
    for im in request.FILES.values():
        try:
            lat, lon, alt = get_gps_coordinates_from_meta_data(image_path=im.file.name)
            gps_data["gps_array"].append({'lat': lat, 'lon': lon, 'alt': alt})
        except LookupError:
            gps_data['gps_data_found'] = False
            # TODO - display this in the app
            print (f"skipping image {im.file.name} since it doesn't have the required GPS meta data")

    json_response = JsonResponse(json.dumps(gps_data), safe=False)  # TODO - is it OK to have safe=False?

    return json_response