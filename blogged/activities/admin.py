from django.contrib import admin

from .models import Activity, TransportWalking
from .models import ActivityInvasiveSpeciesRemoval
from .models import ActivityTreePlantingSession
from .models import ActivityVoleGuardRemoval
from .models import TransportCar
from .models import TransportPublic
from .models import TreePlanting
from .models import TreeSpecies

admin.site.register(Activity)
admin.site.register(TreeSpecies)
admin.site.register(TreePlanting)
admin.site.register(ActivityTreePlantingSession)
admin.site.register(ActivityVoleGuardRemoval)
admin.site.register(ActivityInvasiveSpeciesRemoval)
admin.site.register(TransportCar)
admin.site.register(TransportPublic)
admin.site.register(TransportWalking)
