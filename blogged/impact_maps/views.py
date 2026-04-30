import markdown
from pathlib import Path

from activities.models import Activity
from activities.models import TransportCar
from activities.models import TransportPublic
from activities.models import TransportWalking
from activities.models import TreePlanting
from blog.models import GpsCoordinates
from common.utils import get_secret
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
# Create your views here.


# TODO : Use different API keys for development and production
GOOGLE_MAPS_API_KEY_DEVELOPMENT = get_secret("GOOGLE_MAPS_API_KEY_DEVELOPMENT")


def upload_location(request):
    if request.method == "POST":
        pass

    gps_coordinates = []
    for point in GpsCoordinates.objects.select_related("post").prefetch_related(
        "post__activities", "post__images_set"
    ):
        pin_style = Activity.get_pin_style()
        for activity in point.post.activities.all():
            activity_pin_style = activity.get_pin_style()
            if activity_pin_style != pin_style:
                pin_style = activity_pin_style
                break

        main_image = next(
            (img for img in point.post.images_set.all() if img.is_main_image),
            point.post.images_set.first(),
        )
        thumbnail_url = main_image.public_url if main_image else None

        gps_coordinates.append(
            {
                "latitude": point.latitude,
                "longitude": point.longitude,
                "post_title": point.post.title,
                "post_url": reverse(
                    "detail", kwargs={"slug": point.post.slug, "id": point.post.id}
                ),
                "pin_style": pin_style,
                "thumbnail_url": thumbnail_url,
            }
        )

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

    for t in TransportWalking.objects.all():
        transport_dict["Walking"] = t.distance

    trees_planted_dict = {}
    for tp in TreePlanting.objects.all():
        species = tp.species.common_name
        if species not in trees_planted_dict:
            trees_planted_dict[species] = 0
        trees_planted_dict[species] += tp.quantity
    trees_planted_total = sum(trees_planted_dict.values())

    md_path = (
        Path(__file__).parent
        / "templates"
        / "impact_maps"
        / "impact-summary-background.md"
    )
    impact_summary_html = mark_safe(markdown.markdown(md_path.read_text()))

    return render(
        request,
        "impact_maps/impact-map.html",
        {
            "gps_coordinates": gps_coordinates,
            "impact_summary_html": impact_summary_html,
            "GOOGLE_MAPS_API_KEY": GOOGLE_MAPS_API_KEY_DEVELOPMENT,
            "activity_hours_dict": activity_hours_dict,
            "activity_hours_total": activity_hours_total,
            "trees_planted_dict": trees_planted_dict,
            "trees_planted_total": trees_planted_total,
            "transport_dict": transport_dict,
            "liftshare_dict": liftshare_dict,
        },
    )
