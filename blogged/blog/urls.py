from django.urls import path

from blog.api_views import PostListAPI
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path as url

from .views import ActivityAutocomplete, OrganisationAutocomplete

urlpatterns = [
    path("blog-image-gallery/", views.blog_image_gallery, name="blog-image-gallery"),
    path("upload-post/", views.upload_post, name="upload-post"),
    path("upload-location/", views.upload_location, name="upload-location"),
    path("upload-image/", views.upload_image, name="upload-image"),
    path("extract-gps-coordinates-script/", views.handle_extract_gps_coords),
    path("article/<slug:slug>-<int:id>/", views.detail, name="detail"),
    url(
        'activity-tag-autocomplete/',
        ActivityAutocomplete.as_view(),
        name='activity-tag-autocomplete',
    ),
    url(
        'organisation-tag-autocomplete/',
        OrganisationAutocomplete.as_view(),
        name='organisation-tag-autocomplete',
    ),
    path("", views.index, name="index"),
    path("api/posts/", PostListAPI.as_view(), name="api_post_filter"),
]

# these settings should not be used in prod
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
