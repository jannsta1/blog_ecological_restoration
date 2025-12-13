from django.contrib import admin

# Register your models here.
from .models import Post, Comment, MediaAttachment, Images, GpsCoordinates

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(MediaAttachment)
admin.site.register(Images)
admin.site.register(GpsCoordinates)
