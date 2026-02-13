import logging
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml
from activities.models import Activity
from activities.models import ActivityInvasiveSpeciesRemoval
from activities.models import ActivitySurveying
from activities.models import ActivityTreePlantingSession
from activities.models import ActivityVoleGuardRemoval
from activities.models import TransportCar
from activities.models import TransportPublic
from activities.models import TreePlanting
from activities.models import TreeSpecies
from blog.models import GpsCoordinates
from blog.models import Images
from blog.models import Organisation
from blog.models import Post
from django.core.files import File
from image_processing.meta_data_processing import get_gps_coordinates_from_meta_data
from scripts.resize_images import (
    resize_images_from_path,
    DEFAULT_LARGEST_DIMENSION_SIZE,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PhotoData:
    full_path: Path
    caption: str = ""
    is_main_image: bool = False

    @property
    def name(self) -> str:
        return self.full_path.name

    @property
    def stem(self) -> str:
        return self.full_path.stem


def run(*args, **options):
    # Base directory for photos
    base_photo_dir = Path("/mnt/c/Users/janns/OneDrive/EcoBlogData/photos")
    dry_run = options.get("dry_run", False)
    start_date = options.get("start_date", date(2000, 1, 1))
    end_date = options.get("end_date", date(2200, 1, 1))
    # start_date = options.get("start_date", date(2025, 9, 25))
    # end_date = options.get("end_date", date(2025, 9, 30))

    # resize all images in the photos folder to a maximum dimension of 1200px before processing
    # TODO - we should provide a warning before doing this - perhaps change to an interactive click utility?
    resize_images_from_path(
        base_photo_dir, largest_dimension_size=DEFAULT_LARGEST_DIMENSION_SIZE
    )

    # Get list of data folders
    data_folders = extract_data_folders(base_photo_dir)

    # iterate through each folder
    for day_dir, post_date in data_folders:
        if post_date < start_date or post_date > end_date:
            logger.info(f"Skipping folder {day_dir} outside date range.")
            continue

        title, content = extract_title_and_content(day_dir)
        if not title or not content:
            logger.warning(
                f"Skipping folder {day_dir} due to missing title or content."
            )
            continue

        if dry_run:
            logger.info(
                f"[Dry Run] Would create post titled '{title}' dated {post_date}"
            )
            continue

        # create a Post object with the title, date and content
        post, created = Post.objects.get_or_create(
            title=title,
            date=post_date,
        )

        if created:
            logger.info(f"Created new post: '{title}' dated {post_date}")
            post.content = content
            post.save()
        else:
            logger.info(f"Post already exists: '{title}' dated {post_date}")

            for activity in post.activities.all():
                activity.delete()

            post.delete()
            logger.info(
                f"Deleted existing post to recreate: '{title}' dated {post_date}"
            )
            post = Post.objects.create(title=title, date=post_date, content=content)
            logger.info(f"Recreated post: '{title}' dated {post_date}")

        # load activity yaml if exists
        details_file = day_dir / "details.yaml"

        with open(details_file, "r", encoding="utf-8") as f:
            details_data = yaml.safe_load(f)

        process_activity_data(post, details_data["activity"])
        # # Harvest the 'post' field from details.yaml and update the Post model
        process_post_data(post, details_data["post"])
        process_photo_data(details_data=details_data, data_dir=day_dir, post=post)
        process_transport_data(details_data=details_data, post=post)


def process_transport_data(details_data: dict, post: Post):
    """
    Process transport data from YAML and create Transport models.
    """
    transport_data = details_data.get("transport")
    if transport_data is None:
        return

    for transport_entry in transport_data:
        mode = transport_entry.get("mode")
        distance = transport_entry.get("distance")
        carbon_offset = transport_entry.get("carbon_offset", False)

        if mode == "car":
            TransportCar.objects.create(
                activity=post.activities.first(),  # assuming one activity per post for simplicity
                distance=distance,
                carbon_offset=carbon_offset,
                powertrain=transport_entry.get("powertrain"),
                passengers=transport_entry.get("passengers", 0),
            )
            logger.info(
                f"Added car transport: {distance} km, carbon offset: {carbon_offset}"
            )
        elif mode == "public":
            TransportPublic.objects.create(
                activity=post.activities.first(),  # assuming one activity per post for simplicity
                distance=distance,
                carbon_offset=carbon_offset,
                type=transport_entry.get("type"),
            )
            logger.info(
                f"Added public transport: {distance} km, carbon offset: {carbon_offset}"
            )
        else:
            logger.warning(f"Unknown transport mode: {mode}")


def process_photo_data(
    details_data: dict, data_dir: Path, post: Post
) -> list[PhotoData]:
    """
    Process photo data from YAML and return a list of PhotoData objects.
    """

    photos_data = details_data.get("photos")
    if photos_data is None:
        return []

    # # load photos from the folder - look for image files that are also in details.yaml
    photo_files = (
        list(data_dir.glob("*.jpg"))
        + list(data_dir.glob("*.jpeg"))
        + list(data_dir.glob("*.png"))
    )
    photo_names = {p["name"]: p for p in photos_data}
    selected_photos = [p for p in photo_files if p.stem in photo_names.keys()]
    # TODO: warn if photos in details.yaml are missing from folder

    photos = []
    for photo in selected_photos:
        photo_detail = photo_names.get(photo.stem)
        photo_obj = PhotoData(
            full_path=photo,
            caption=photo_detail["caption"],
            is_main_image=photo_detail.get("is_main_image", False),
        )
        photos.append(photo_obj)

    for photo_data in photos:
        # check if an Images object already exists for this post and filename

        # if photo_file.stem not in photo_names:
        #     logger.warning(f"Photo file {photo_file.name} not listed in details.yaml for post '{post.title}'. Skipping.")
        #     continue

        existing_image = Images.objects.filter(
            post=post, image__icontains=photo_data.name
        ).first()
        if existing_image:
            logger.info(
                f"Image already exists for post '{post.title}': {photo_data.name}. Skipping."
            )
            continue

        try:
            with open(photo_data.full_path, "rb") as img_file:
                image = Images.objects.create(
                    post=post,
                    caption=photo_data.caption,
                    is_main_image=photo_data.is_main_image,
                )
                try:
                    create_gps_coordinates(post=post, image_path=photo_data.full_path)
                except LookupError:
                    logger.info(
                        f"No GPS data found in image {photo_data.name} for post '{post.title}' - saving anyway."
                    )
                image.image.save(photo_data.name, File(img_file), save=True)
                logger.info(f"Added image to post '{post.title}': {photo_data.name}")

        except Exception as e:
            logger.error(
                f"Error adding image {photo_data.name} to post '{post.title}': {e}"
            )


def process_post_data(post: Post, post_data: dict):
    """
    Process post data from YAML and update the Post model.
    """
    post.status = post_data.get("status", "DR")

    # Update organisation_tags if present
    #  Direct assignment to the forward side of a many-to-many set is prohibited. Use organisation_tags.set() instead.
    org_data = post_data.get("organisation_tags")
    org_ids = []
    for org in org_data:
        name_tag = org["tag"]
        org_tag = Organisation.objects.get(name=name_tag)
        if org_tag is None:
            logger.info(f"Could not find organisation tag: {name_tag}")
            continue
        org_ids.append(org_tag.id)
        logger.info(f"Saving tag: {org_tag.name} with id {org_tag.id}")

    post.organisation_tags.set(org_ids)

    # Update generic tags if they are present
    tags = post_data.get("tags")
    if tags:
        post.tags.set(tags)
    post.save()


def extract_data_folders(base_photo_dir) -> list[tuple[Path, date]]:
    """
    Extract date folders from the photos directory structure.
    Assemble the date from the folder (day), its parent folder (month) and its grandparent folder (year)

    Returns:
        List of tuples: (directory, year, month, day)
    """
    data_folders = []

    for year_dir in sorted(base_photo_dir.iterdir()):
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue

        year = year_dir.name

        for month_dir in sorted(year_dir.iterdir()):
            if not month_dir.is_dir() or not month_dir.name.isdigit():
                continue

            month = month_dir.name

            for day_dir in sorted(month_dir.iterdir()):
                if not day_dir.is_dir() or not day_dir.name.isdigit():
                    continue

                day = day_dir.name

                try:
                    post_date = date(int(year), int(month), int(day))
                except ValueError as e:
                    logger.warning(
                        f"Invalid date from folder structure {year}/{month}/{day}: {e}"
                    )
                    continue
                data_folders.append((day_dir, post_date))

    return data_folders


def extract_title_and_content(day_dir: Path) -> tuple[str, str]:
    """
    Extract title and content from the content.md file in the given directory.
    If the file does not exist, return a default title and empty content.

    Returns:
        title (str), content (str)
    """
    content_file = day_dir / "content.md"
    if content_file.exists():
        with open(content_file, "r", encoding="utf-8") as f:
            content = f.read()

        # load the file "content.md" into a variable `content` if the file exists, if it does not exist, log a warning message and skip this folder
        content_file = day_dir / "content.md"

        with open(content_file, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            logger.warning(f"Empty content in {content_file}. Skipping.")
            return None, None

        # extract the first line of the content as the title
        lines = content.split("\n")
        title = lines[0]
        content = content.lstrip(title).strip()
        title = title.lstrip("#").strip()

        if not title or not content:
            logger.warning(f"Empty title in {content_file}. Skipping.")
            return None, None
    else:
        logger.warning(
            f"Missing content.md in {day_dir}. Using default title and empty content."
        )
        return None, None

    return title, content


def process_activity_data(post: Post, activity_data: dict):
    """
    Process activity data from YAML and create appropriate activity models.
    """
    if "tree_planting_session" in activity_data:
        activity = process_tree_planting_session(post, activity_data)
    elif "vole_guard_removal" in activity_data:
        activity = process_vole_guard_removal(post, activity_data)
    elif "invasive_species_removal" in activity_data:
        activity = process_invasive_species_removal(post, activity_data)
    elif "survey" in activity_data:
        activity = process_survey_activity(post, activity_data)
    else:
        activity = process_generic_activity(post, activity_data)

    activity.location = activity_data.get("location")
    activity.hours_spent = activity_data.get("hours", 0)
    activity.save()

    logger.info(f"Processed activity data for post '{post.title}'")


def process_generic_activity(post: Post, activity_data: dict):
    """
    Create a generic Activity object.
    """
    logger.info("Added generic activity")
    return Activity.objects.create(post=post)


def process_survey_activity(post: Post, activity_data: dict):
    """
    Create a Survey Activity object.
    """
    # survey_data = activity_data.get("survey")
    # Assuming ActivitySurvey is defined similarly to other activity models
    logger.info("Added survey activity")
    return ActivitySurveying.objects.create(post=post)


def process_tree_planting_session(post: Post, activity_data: dict):
    """
    Create ActivityTreePlantingSession and associated TreePlanting objects.
    """
    # Extract location if provided

    session_data = activity_data["tree_planting_session"]
    notes = session_data.get("notes")

    # Create the tree planting session
    activity = ActivityTreePlantingSession.objects.create(post=post, notes=notes)

    # Process tree plantings
    tree_plantings = session_data.get("tree_planting", [])
    for planting_data in tree_plantings:
        trees_planted_name = planting_data.get("trees_planted")
        quantity = planting_data.get("quantity")
        planting_style_str = planting_data.get("planting_style", "Plug")

        if not trees_planted_name or not quantity:
            logger.warning(f"Incomplete tree planting data: {planting_data}")
            continue

        # Try to find the species - could be common name or "Genus Species"
        species = None

        # First try as common name
        species = TreeSpecies.objects.filter(
            common_name__iexact=trees_planted_name
        ).first()

        # If not found, try parsing as "Genus SpecificEpithet"
        if not species:
            parts = trees_planted_name.split()
            if len(parts) >= 2:
                genus = parts[0]
                specific_epithet = " ".join(parts[1:])
                species = TreeSpecies.objects.filter(
                    genus__iexact=genus, specific_epithet__iexact=specific_epithet
                ).first()

        if not species:
            logger.warning(f"Could not find species: {trees_planted_name}")
            continue

        # Map planting style string to enum
        planting_style = TreePlanting.PlantingStyle.PLUG
        if planting_style_str.lower() in ["bareroot", "bare root"]:
            planting_style = TreePlanting.PlantingStyle.BAREROOT

        # Create tree planting
        TreePlanting.objects.create(
            trees_planted=activity,
            quantity=quantity,
            species=species,
            planting_style=planting_style,
            gps_data=planting_data.get("gps_data"),
        )
        logger.info(f"Added tree planting: {quantity} x {species.common_name}")

    return activity


def process_vole_guard_removal(post: Post, activity_data: dict):
    """
    Create ActivityVoleGuardRemoval object.
    """

    removal_data = activity_data["vole_guard_removal"]
    area_covered = removal_data.get("area_covered")
    plastic_removed = removal_data.get("plastic_removed")
    trees_liberated = removal_data.get("trees_liberated")
    gps_track = removal_data.get("gps_track")

    if not area_covered:
        logger.warning("Missing required field 'area_covered' for vole guard removal")
        return

    logger.info("Added vole guard removal activity")
    return ActivityVoleGuardRemoval.objects.create(
        post=post,
        area_covered=area_covered,
        plastic_removed=plastic_removed,
        trees_liberated=trees_liberated,
        gps_track=gps_track,
    )


def process_invasive_species_removal(post: Post, activity_data: dict):
    """
    Create ActivityInvasiveSpeciesRemoval object.
    """
    removal_data = activity_data["invasive_species_removal"]

    species_removed_name = removal_data.get("species_removed")
    quantity_removed = removal_data.get("quantity_removed")
    gps_track = removal_data.get("gps_track")

    if not species_removed_name or not quantity_removed:
        logger.warning("Missing required fields for invasive species removal")
        return

    # Find the species
    species = TreeSpecies.objects.filter(
        common_name__iexact=species_removed_name
    ).first()

    if not species:
        # Try parsing as "Genus SpecificEpithet"
        parts = species_removed_name.split()
        if len(parts) >= 2:
            genus = parts[0]
            specific_epithet = " ".join(parts[1:])
            species = TreeSpecies.objects.filter(
                genus__iexact=genus, specific_epithet__iexact=specific_epithet
            ).first()

    if not species:
        logger.warning(f"Could not find species: {species_removed_name}")
        return

    logger.info(f"Added invasive species removal activity: {species.common_name}")
    return ActivityInvasiveSpeciesRemoval.objects.create(
        post=post,
        species_removed=species,
        quantity_removed=quantity_removed,
        gps_track=gps_track,
    )


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
