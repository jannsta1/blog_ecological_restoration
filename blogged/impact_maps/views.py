from django.shortcuts import render

# Create your views here.
from blog.models import GpsCoordinates
from common.utils import get_secret


# TODO : Use different API keys for development and production
GOOGLE_MAPS_API_KEY_DEVELOPMENT = get_secret("GOOGLE_MAPS_API_KEY_DEVELOPMENT")


def upload_location(request):
    if request.method == "POST":
        pass

    gps_coordinates = {
        "gps_coordinates": list(GpsCoordinates.objects.values("latitude", "longitude")),
        "GOOGLE_MAPS_API_KEY": GOOGLE_MAPS_API_KEY_DEVELOPMENT,
    }  # values returns dictionaries rather than objects
    return render(request, "impact_maps/impact-map.html", gps_coordinates)
