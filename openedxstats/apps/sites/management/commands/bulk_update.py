"""Management command to update many sites at once, from census.py"""

import json
import sys

from django.core.management.base import BaseCommand

from openedxstats.apps.sites.models import Site, OverCount

class Command(BaseCommand):
    help = "Update many sites at once from update.json written by census.py"

    def handle(self, *args, **options):
        updates = json.load(sys.stdin)
        print(type(updates))
        print(len(updates))
        print(updates.keys())
        print(len(updates['sites']))
