import json

from activities.models import TreeSpecies
from django.core.management.base import BaseCommand
from settings.common import BASE_DIR

with open(BASE_DIR / "../data/tree_species.json") as f:
    tree_data = json.load(f)


# TODO: add a flag to replace existing entries
#       look for duplicates based on genus + specific_epithet
class Command(BaseCommand):
    def handle(self, *args, **options):
        # add trees
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
