from django.test import TestCase
from management.commands.import_lang_geo import import_data

CSV_FILE = '~/Documents/postgres_data/edx_lang_geo_csv.csv'

class ImportScriptTestCase(TestCase):

    def test_import_languages_and_geozones_from_file(self):
        with open(CSV_FILE, 'rwb') as csvfile:
            import_data(csvfile) # Import data

