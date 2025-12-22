import os

from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import slugify
from storages.backends.gcloud import GoogleCloudStorage
from django.urls import reverse
# from gdstorage.storage import GoogleDriveStorage


# Define Google Drive Storage
# gd_storage = GoogleDriveStorage()
gc_storage = GoogleCloudStorage()

class Activity(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Organisation(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# Create your models here.
class Post(models.Model):
    MAX_SLUG_LENGTH = 60

    title = models.CharField(max_length=255)
    date = models.DateField()
    slug = models.SlugField(
        null=False,
        max_length=MAX_SLUG_LENGTH,
        # unique=True,  NOTE - we instead protect against duplicates by having the Post id in the URL
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    activities_tag = models.ManyToManyField(Activity, blank=True, related_name='custom_activity_tags')
    organisation_tags = models.ManyToManyField(Organisation, blank=True, related_name='custom_organisation_tags')

    def save(self, *args, **kwargs):
        """
        We create the slug automatically from the title - the spaces are replaced with hyphens and it is truncated to MAX_SLUG_LENGTH.
        """
        if not self.slug:
            self.slug = slugify(getattr(self, "title"))[:self.MAX_SLUG_LENGTH]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"slug": self.slug, "id": self.pk})

    class Meta:
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return self.title


def get_image_filename(instance, filename):
    id = instance.post.id
    database_tag = os.environ.get("PROJECT_DB_TAG")
    if database_tag is None:
        raise ValueError("Missing required env: PROJECT_DB_TAG")

    return f"rewilding/images/{database_tag}/{id}/{filename}"


class Images(models.Model):
    post = models.ForeignKey(Post, default=None, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to=get_image_filename, storage=gc_storage, verbose_name="Image"
    )
    caption = models.TextField(null=True, blank=True)

    @property
    def public_url(self):
        """
        For the google cloud API there is the 'public' and 'authenticated' address for images.

        Experiments showed that the authenticated API is stored by django-storage but only the public address is accessible.
        This properties provides a way to access the working public address.

        """

        url = self.image.url
        return url.replace(
            "https://storage.googleapis.com", "https://storage.cloud.google.com"
        )


class GpsCoordinates(models.Model):
    post = models.ForeignKey(Post, default=None, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField()

    def clean(self):
        super().clean()

        if not self.latitude:
            raise ValidationError({"latitude": "latitude field cannot be empty."})
        if not self.longitude:
            raise ValidationError({"longitude": "longitude field cannot be empty."})
        if not self.altitude:
            raise ValidationError({"altitude": "altitude field cannot be empty."})
