from activities.models import Activity, Transport, TransportCar, TransportPublic
from activities.models import TreePlanting
from blog.models import GpsCoordinates
from common.utils import get_secret
from django.shortcuts import render
# Create your views here.


# TODO : Use different API keys for development and production
GOOGLE_MAPS_API_KEY_DEVELOPMENT = get_secret("GOOGLE_MAPS_API_KEY_DEVELOPMENT")


def upload_location(request):
    if request.method == "POST":
        pass

    gps_coordinates = list(GpsCoordinates.objects.values("latitude", "longitude"))

    activity_hours_dict = {}
    for a in Activity.objects.all():
        category = a.activity_type.label
        if category not in activity_hours_dict:
            activity_hours_dict[category] = 0
        if a.hours_spent is not None:
            activity_hours_dict[category] += a.hours_spent
    activity_hours_total = sum(activity_hours_dict.values())

    transport_dict = {}
    liftshare_dict = {}
    for t in TransportCar.objects.all():        

        category = "Car - " + TransportCar.Powertrain(t.powertrain).label
        if category not in transport_dict:
            transport_dict[category] = 0
            
        if t.passengers > 0:
            if category not in liftshare_dict:
                liftshare_dict[category] = 0
            liftshare_dict[category] += t.distance * t.passengers
        transport_dict[category] += t.distance 

    

    for t in TransportPublic.objects.all():        
        category = "Public Transport - " + TransportPublic.Type(t.type).label
        transport_dict[category] = t.distance

    trees_planted_dict = {}
    for tp in TreePlanting.objects.all():
        species = tp.species.common_name
        if species not in trees_planted_dict:
            trees_planted_dict[species] = 0
        trees_planted_dict[species] += tp.quantity
    trees_planted_total = sum(trees_planted_dict.values())

    return render(
        request,
        "impact_maps/impact-map.html",
        {
            "gps_coordinates": gps_coordinates,
            "GOOGLE_MAPS_API_KEY": GOOGLE_MAPS_API_KEY_DEVELOPMENT,
            "activity_hours_dict": activity_hours_dict,
            "activity_hours_total": activity_hours_total,
            "trees_planted_dict": trees_planted_dict,
            "trees_planted_total": trees_planted_total,
            "transport_dict": transport_dict,
            "liftshare_dict": liftshare_dict,
        },
    )
