import json

from blog.models import Organisation
from django.core.management.base import BaseCommand
from settings.common import BASE_DIR


with open(BASE_DIR / "../data/organisations.json") as f:
    organisations = json.load(f)


class Command(BaseCommand):
    def handle(self, *args, **options):
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
