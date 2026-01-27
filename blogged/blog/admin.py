from django.contrib import admin

from .models import GpsCoordinates
from .models import Images
from .models import Organisation
from .models import Post

admin.site.register(Organisation)
admin.site.register(Post)
admin.site.register(Images)
admin.site.register(GpsCoordinates)
