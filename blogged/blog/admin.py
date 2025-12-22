from django.contrib import admin

from .models import GpsCoordinates
from .models import Images
from .models import Post
from .models import Activity
from .models import Organisation

admin.site.register(Organisation)
admin.site.register(Activity)
admin.site.register(Post)
admin.site.register(Images)
admin.site.register(GpsCoordinates)
