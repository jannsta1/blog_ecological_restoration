from django.contrib import admin

from .models import GpsCoordinates
from .models import Images
from .models import Videos
from .models import Organisation
from .models import Post

admin.site.register(Organisation)
admin.site.register(Post)
admin.site.register(Images)
admin.site.register(Videos)
admin.site.register(GpsCoordinates)
