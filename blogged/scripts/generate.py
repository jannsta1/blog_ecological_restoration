import json

from activities.models import TreeSpecies
from blog.models import Organisation
from settings.common import BASE_DIR

from scripts.add_posts import create_tree_planting_activity
from scripts.add_posts import create_vole_guard_activity

with open(BASE_DIR / "../data/organisations.json") as f:
    organisations = json.load(f)

with open(BASE_DIR / "../data/tree_species.json") as f:
    tree_data = json.load(f)


def run():
    # create tree species
    for species_key, species_info in tree_data.items():
        species, created = TreeSpecies.objects.get_or_create(
            genus=species_info["genus"],
            specific_epithet=species_info["specific_epithet"],
            defaults={"common_name": species_info["common_name"]},
        )
        if created:
            print(
                f"Added new species: {species.common_name} ({species.genus} {species.specific_epithet})"
            )
        else:
            print(
                f"Species already exists: {species.common_name} ({species.genus} {species.specific_epithet})"
            )

    # create organisations
    for org_code, org_info in organisations.items():
        org, created = Organisation.objects.get_or_create(
            name=org_info["name"],
            website=org_info["website"],
            description=org_info["description"],
        )
        if created:
            print(f"Created organisation: {org.name}")
        else:
            print(f"Organisation already exists: {org.name}")

    # create example posts
    create_tree_planting_activity()
    create_vole_guard_activity()
