from django.contrib import admin

from .models import GpsCoordinates
from .models import Images
from .models import Post
# Register your models here.

admin.site.register(Post)
admin.site.register(Images)
admin.site.register(GpsCoordinates)
