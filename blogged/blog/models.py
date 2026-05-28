import os

from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from storages.backends.gcloud import GoogleCloudStorage
from taggit.managers import TaggableManager
from django_cleanup import cleanup
from django.core.validators import FileExtensionValidator
# from gdstorage.storage import GoogleDriveStorage

# Define Google Drive Storage
# gd_storage = GoogleDriveStorage()
gc_storage = GoogleCloudStorage()


class Organisation(models.Model):
    # TODO - add enum class here for the organisation types?
    name = models.CharField(max_length=100, unique=True)
    website = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


# Create your models here.
class Post(models.Model):
    MAX_SLUG_LENGTH = 60

    class ArticleStatus(models.TextChoices):
        DRAFT = "DR", "Draft"
        PUBLISHED = "PU", "Published"
        ARCHIVED = "AR", "Archived"

    status = models.CharField(
        max_length=2,
        choices=ArticleStatus.choices,
        default=ArticleStatus.DRAFT,
    )

    title = models.CharField(max_length=255)
    date = models.DateField()
    slug = models.SlugField(
        null=False,
        max_length=MAX_SLUG_LENGTH,
        # unique=True,  NOTE - we instead protect against duplicates by having the Post id in the URL
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    revision = models.IntegerField(
        default=1
    )  # TODO - implement the mechanism to increment this on save

    organisation_tags = models.ManyToManyField(
        Organisation, blank=True, related_name="custom_organisation_tags"
    )
    tags = TaggableManager(blank=True)

    def save(self, *args, **kwargs):
        """
        We create the slug automatically from the title - the spaces are replaced with hyphens and it is truncated to MAX_SLUG_LENGTH.
        """
        if not self.slug:
            self.slug = slugify(getattr(self, "title"))[: self.MAX_SLUG_LENGTH]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("detail", kwargs={"slug": self.slug, "id": self.pk})

    class Meta:
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return self.title

    @property
    def word_count(self):
        """
        Returns the word count of the post content.

        TODO - can we cache this value and only recalculate when the content changes?
        """
        return len(self.content.split())

    @property
    def post_activities(self):
        """
        Returns a list of unique activity types associated with this post via activities.

        TODO - cache this value and only recalculate when activity updates
        """
        if self.activities.all():
            return [tag.activity_type.label for tag in self.activities.all()]
        return []

    @property
    def organisations(self):
        """
        Returns a list of unique organisations associated with this post via organisation_tags.
        """
        return [org.name for org in self.organisation_tags.all()]

    # @property
    # def activity_locations(self):
    #     """
    #     Returns a list of unique activity locations associated with this post via activities.
    #     """
    #     locations = Post.activities.values_list('location', flat=True).distinct()
    #     return list(locations)


def get_image_filename(
    instance, filename
):  # TODO - this is also used for videos - should we rename it to get_media_filename?
    id = instance.post.id
    database_tag = os.environ.get("PROJECT_DB_TAG")
    if database_tag is None:
        raise ValueError("Missing required env: PROJECT_DB_TAG")

    return f"rewilding/images/{database_tag}/{id}/{filename}"


# Adding this decorator ensures that when an Images instance is deleted, the associated image file is also deleted from google storage bucket
@cleanup.select
class Images(models.Model):
    """
    Docstring for Images

    is_featured: intended as a way to select photos that are attractive vs those that are documentative e.g. planting sites
    """

    post = models.ForeignKey(Post, default=None, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to=get_image_filename,
        storage=gc_storage,
        verbose_name="Image",
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "gif"])
        ],
    )
    thumbnail = ImageSpecField(
        source="image",
        processors=[ResizeToFill(100, 100)],
        format="JPEG",
        options={"quality": 60},
    )
    is_main_image = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    caption = models.TextField(null=True, blank=True)
    attribution = models.CharField(
        max_length=255, null=True, blank=True, default="Jan Stankiewicz"
    )
    media_type = "IMAGE"  # TODO - this is a way to distinguish between images and videos in templates - could use a more principled method like having a Media parent class that both Images and Videos inherit from

    @property
    def public_thumbnail_url(self):
        """
        For the google cloud API there is the 'public' and 'authenticated' address for images.
        """
        url = self.thumbnail.url
        return url.replace(
            "https://storage.googleapis.com", "https://storage.cloud.google.com"
        )

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


@cleanup.select
class Videos(models.Model):
    # TODO - we may also want to embed form other sources like youtube?
    # TODO - should we make a Media abstract class and have Images and Videos inherit from it? (since they share some fields like caption, attribution, is_featured)
    post = models.ForeignKey(Post, default=None, on_delete=models.CASCADE)
    video = models.FileField(
        upload_to=get_image_filename,
        storage=gc_storage,
        verbose_name="Video",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["MOV", "avi", "mp4", "webm", "mkv"]
            )
        ],
    )  # TODO - 1) add further validation to ensure only video files are uploaded 2) keep these extensions in a variable for use elsewhere
    is_featured = models.BooleanField(default=False)
    caption = models.TextField(null=True, blank=True)
    attribution = models.CharField(
        max_length=255, null=True, blank=True, default="Jan Stankiewicz"
    )
    media_type = "VIDEO"

    @property
    def public_url(self):
        """
        For the google cloud API there is the 'public' and 'authenticated' address for videos.

        Experiments showed that the authenticated API is stored by django-storage but only the public address is accessible.
        This properties provides a way to access the working public address.

        """
        url = self.video.url
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
