from activities.models import Activity
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
        activity_hours_dict[category] += a.hours_spent
    activity_hours_total = sum(activity_hours_dict.values())

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
        },
    )
