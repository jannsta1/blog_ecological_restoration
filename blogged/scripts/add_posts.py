import os
from pathlib import Path

import django
from activities.models import ActivityTreePlantingSession
from activities.models import ActivityVoleGuardRemoval
from activities.models import Location
from activities.models import TransportCar
from activities.models import TreePlanting
from activities.models import TreeSpecies
from blog.models import GpsCoordinates
from blog.models import Images
from blog.models import Organisation
from blog.models import Post
from django.core.files import File
from image_processing.meta_data_processing import get_gps_coordinates_from_meta_data


# e.g.: dm runscript gps_from_image --script-args /home/jan/dev/blog_ecological_restoration/data/photos/2025/05/04/PXL_20250504_120358738.jpg
def run(*args, **options):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blogged.settings.production")
    django.setup()
    # Example: Create a blog post for a tree planting activity with associated data
    create_tree_planting_activity_with_photos(*args, **options)
    create_tree_planting_activity(*args, **options)
    create_vole_guard_activity(*args, **options)


def create_gps_coordinates(post: Post, image_path: Path, *args, **options):
    lat, lon, alt = get_gps_coordinates_from_meta_data(image_path=image_path)

    # gps_data = {"gps_array": []}
    # gps_data["gps_array"].append({"lat": lat, "lon": lon, "alt": alt})
    gps_coordinate = GpsCoordinates.objects.create(
        post=post,
        latitude=lat,
        longitude=lon,
        altitude=alt,
        # raw_gps_data=gps_data,
    )
    gps_coordinate.save()


def create_tree_planting_activity_with_photos(*args, **options):
    organisation = Organisation.objects.get(name="Borders Forest Trust")
    # Create the blog post
    post, created = Post.objects.get_or_create(
        title="Tree Planting Activity at Talla with photos",
        date="2024-06-15",
        content="We had a successful tree planting session at Talla...",
    )
    post.organisation_tags.add(organisation)

    if not created:
        post.delete()
        print("Blog post already exists. Recursing to recreate.")
        create_tree_planting_activity_with_photos(*args, **options)
        return

    if created:
        # Create the activity
        activity = ActivityTreePlantingSession.objects.create(
            post=post,
            location=Location.TALLA,  # Talla & Gameshope
        )

        species_oak = TreeSpecies.objects.get(common_name="English Oak")

        TreePlanting.objects.create(
            trees_planted=activity,
            quantity=100,
            species=species_oak,
            gps_data={"type": "Point", "coordinates": [-3.12345, 55.12345]},
        )

        image_path = "/home/jan/dev/blog_ecological_restoration/data/photos/2024/02/04/PXL_20240204_115446467.jpg"
        with open(image_path, "rb") as img_file:
            image = Images.objects.create(
                post=post, caption="My precious trees", is_main_image=True
            )
            create_gps_coordinates(post=post, image_path=Path(image_path))
            image.image.save(os.path.basename(image_path), File(img_file), save=True)

        # print(image.public_thumbnail_url)
        print(image.public_url)


def create_tree_planting_activity(*args, **options):
    # get an organisation tag
    organisation = Organisation.objects.first()

    # Create the blog post
    post, created = Post.objects.get_or_create(
        title="Tree Planting Activity at Talla",
        date="2024-06-15",
        content="We had a successful tree planting session at Talla...",
    )
    post.organisation_tags.add(organisation)

    if not created:
        post.delete()
        print("Blog post already exists. Recursing to recreate.")
        create_tree_planting_activity(*args, **options)
        return

    if created:
        # Create the activity
        activity = ActivityTreePlantingSession.objects.create(
            post=post,
            location=Location.TALLA,  # Talla & Gameshope
        )

        # Add tree plantings to the activity
        species_ash = TreeSpecies.objects.get(common_name="European Ash")
        species_oak = TreeSpecies.objects.get(common_name="English Oak")

        TreePlanting.objects.create(
            trees_planted=activity,
            quantity=100,
            species=species_ash,
            gps_data={"type": "Point", "coordinates": [-3.12345, 55.12345]},
        )

        TreePlanting.objects.create(
            trees_planted=activity,
            quantity=150,
            species=species_oak,
            gps_data={"type": "Point", "coordinates": [-3.12350, 55.12350]},
        )

        # add transport data
        TransportCar.objects.create(
            activity=activity,
            distance=10.5,
            carbon_offset=True,
            powertrain=TransportCar.Powertrain.ELECTRIC,
        )

        print("Successfully created blog post and associated tree planting activity.")

    else:
        print("Blog post already exists. No new activity created.")


def create_vole_guard_activity(*args, **options):
    # Create the blog post
    organisation = Organisation.objects.get(name="Trees for Life")

    post, created = Post.objects.get_or_create(
        title="Vole Guard Activity at Talla",
        date="2024-06-15",
        content="We had a successful vole guard removal session at Talla...",
    )
    post.organisation_tags.add(organisation)

    if not created:
        post.delete()
        print("Blog post already exists. Recursing to recreate.")
        create_vole_guard_activity(*args, **options)
        return

    if created:
        # Create the activity
        activity = ActivityVoleGuardRemoval.objects.create(
            post=post,
            location=Location.CARRIFRAN,  # Talla & Gameshope
            area_covered=250.0,
            plastic_removed=15.0,
            trees_liberated=200,
            gps_track={
                "type": "LineString",
                "coordinates": [[-3.12345, 55.12345], [-3.12350, 55.12350]],
            },
        )

        # add transport data
        TransportCar.objects.create(
            activity=activity,
            distance=10.5,
            carbon_offset=True,
            powertrain=TransportCar.Powertrain.ELECTRIC,
        )

        print(
            "Successfully created blog post and associated vole guard removal activity."
        )

    else:
        print("Blog post already exists. No new activity created.")
