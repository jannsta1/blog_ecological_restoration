from django.db import models
# from gdstorage.storage import GoogleDriveStorage
from storages.backends.gcloud import GoogleCloudStorage

from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify


# Define Google Drive Storage
# gd_storage = GoogleDriveStorage()
gc_storage = GoogleCloudStorage()


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField()
    slug = models.SlugField(null=False, unique=True)  # TODO - use a uid or something instead to allow blog posts with the same title?
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        We create the slug automatically from the title

        TODO - might be better just to use an ID rather than slug?:
        https://learndjango.com/tutorials/django-slug-tutorial#:~:text=The%20best%20solution%20is%20to,be%20applied%20to%20the%20serializer.
        """                
        self.slug = slugify(getattr(self, 'title'))
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at',]

    def __str__(self):
        return self.title
    

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at',]

    def __str__(self):
        return f'{self.name} - {self.post.title}'
    

class MediaAttachment(models.Model):
    id = models.AutoField( primary_key=True)
    name = models.CharField(max_length=255)
    caption = models.TextField(default="No caption")
    # image = models.ImageField(upload_to='uploaded-images', storage=gd_storage)
    # image = models.ImageField(upload_to='uploaded-images/')
    image = models.ImageField(upload_to='rewilding/images', storage=gc_storage)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    

    def __str__(self):
        return self.name
    
    @property
    def public_url(self):
        """
        For the google cloud API there is the 'public' and 'authenticated' address for images.

        Experiments showed that the authenticated API is stored by django-storage but only the public address is accessible.
        This properties provides a way to access the working public address.

        """

        url = self.image.url
        return url.replace("https://storage.googleapis.com", "https://storage.cloud.google.com")
    

class GoogleBucketAttachment(models.Model):
    
    id = models.AutoField( primary_key=True)
    name = models.CharField(max_length=255)
    # caption = models.TextField(default="No caption")
    image = models.ImageField(upload_to='rewilding/images', storage=gc_storage)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

def get_image_filename(instance, filename):
    id = instance.post.id
    return f"rewilding/images/{id}/{filename}"


class Images(models.Model):
    post = models.ForeignKey(Post, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_image_filename, storage=gc_storage, verbose_name='Image')
    caption = models.TextField(null=True, blank=True)

    @property
    def public_url(self):
        """
        For the google cloud API there is the 'public' and 'authenticated' address for images.

        Experiments showed that the authenticated API is stored by django-storage but only the public address is accessible.
        This properties provides a way to access the working public address.

        """

        url = self.image.url
        return url.replace("https://storage.googleapis.com", "https://storage.cloud.google.com")


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