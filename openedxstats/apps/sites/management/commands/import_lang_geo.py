from django.core.management.base import BaseCommand, CommandError
from ...models import *
import csv

# TODO
# TODO: Make this script work for all data, not just language and geozones!!!
# TODO: Make it idempotent
# TODO: Make it so that it only imports if it doesn't exist
# TODO: Spreadsheet is always right
# TODO

class Command(BaseCommand):
    """
    Allows for import of language and geography data from a csv file to the app database.
    Example command input:  python manage.py import_lang_geo ~/Documents/data.csv
    """

    help = 'Imports language and geography data from a correctly formatted csv file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Specify file to use as source for input data.')

    def handle(self, *args, **options):

        # Open the csv file, and iterate through each row, associating it with the correct site in the database by inserting
        # the data into the junction tables
        with open(options['csv_file'], 'rwb') as csvfile:
            reader = csv.reader(csvfile)
            iter_reader = iter(reader)

            # Make sure the number of rows of sites matches the number of rows of the csv import file
            list_of_sites = Site.objects.all()
            num_sites = len(list_of_sites)
            iter_reader.next()  # Skips header
            input_rows = []
            for row in iter_reader:
                input_rows.append(row)

            # Throw error if row counts do not match
            if num_sites != len(input_rows):
                print("ERROR: Number of rows in sites_site (%s) does not match number of rows in import csv(%s)!"
                      % (num_sites, len(input_rows)))
                return

            print("Numbers match!")
            print("Num_sites = %s \t Num_imports = %s" % (num_sites, len(input_rows)))
            print("Begin import... "),

            # Now, insert data and generate relationships
            for row in input_rows:
                for icol, col in enumerate(row):

                    if not col:
                        continue

                    items = col.split(',')

                    for item in items:
                        if icol == 0:  # We are in the language column
                            language = Language(name=item)
                            language.save()


                            # Insert record into junction table to associate with site
                            site = Site.objects.get(url=list_of_sites[icol].url)
                            site_language = SiteLanguage(language_id=language, site_id=site.id)
                            site_language.save()

                        elif icol == 1:  # We are in the geography column
                            geo_zone = GeoZone(name=item)
                            geo_zone.save()

                            # Insert record into junction table to associate with site
                            site = Site.objects.get(url=list_of_sites[icol].url)
                            site_geozone = SiteGeoZone(geo_zone_id=geo_zone, site_id=site.id)
                            site_geozone.save()

        print("Finished!")
