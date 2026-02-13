import os

import django
from image_processing.meta_data_processing import get_gps_coordinates_from_meta_data


def run(*args, **options):
    impath = args[0]
    image_path = os.path.abspath(impath)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blogged.settings.production")
    django.setup()

    lat, lon, alt = get_gps_coordinates_from_meta_data(image_path=image_path)
    print(f"Lat: {lat} Lon: {lon} Alt: {alt}")
