from django.contrib import admin
from hitcount.models import HitCount
from hitcount.models import UrlHit
# Register your models here.


admin.site.register(UrlHit)
admin.site.register(HitCount)
