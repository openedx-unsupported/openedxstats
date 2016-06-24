from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from ...models import *
import csv
from dateutil import parser
from django.db.models.fields import NOT_PROVIDED


REQUIRED_COLS = ["url"] # Add fields to this list that the csv should have
# HEADER_NAMES = Site.__meta.get_all_field_names.remove("geography").remove("language")
HEADER_NAMES = ["site_type", "name", "url", "course_count", "last_checked", "org_type", "github_fork", "notes",
                "course_type", "registered_user_count", "active_learner_count"]
M2M_HEADER_NAMES = ["geography", "language"]


# TODO: Need to allow for import script to detect column 'last_checked' or 'active_start_date', and put them both
# TODO: into active start date respectively. 



class Command(BaseCommand):
    """
    Allows for import of site data from a csv file to the app database.
    Example command input:  python manage.py import_sites ~/Documents/data.csv

    IMPORTANT NOTES:
    - The csv file's first row MUST be a header row, with all of the column names
    - All rows following the header row should be data
    - The CSV file must at least have the cols in REQUIRED_COLS
    - Data under last_checked must be in a valid date or datetime format, or the parser will raise an error
        - If it is a date, not a datetime, then the parser will raise a warning and set the time to 00:00:00
    """

    help = 'Imports language and geography data from a correctly formatted csv file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Specify file to use as source for input data.')

    def handle(self, *args, **options):
        # Open the csv file
        with open(options['csv_file'], 'r+') as csvfile:
            result_string = import_data(csvfile)
            return result_string


def check_for_required_cols(header_row):
    """
    Checks to make sure that there are required columns in the csv file header_row
    The header_row should be the first row in the csv file
    :param header_row:
    :return:
    """
    required_cols = list(REQUIRED_COLS)
    for col in header_row:
        if col in required_cols:
            required_cols.remove(col)

    if len(required_cols) > 0:
        raise CommandError("Missing required cols in csv file: %s" % required_cols)
    else:
        return


def import_data(csvfile):
    """
    Iterates through each row of the provided csv, creating the appropriate models and saving them to the DB
    :param csvfile:
    :return:
    """
    total_count_stats = {"sites":0, "languages":0, "geozones":0, "site_languages":0, "site_geozones":0}
    reader = csv.reader(csvfile)
    iter_reader = iter(reader)
    try:
        header_row = next(iter_reader)  # Skip header
    except:
        raise CommandError("Empty or improperly configured csv")
    check_for_required_cols(header_row)

    input_rows = []
    for row in iter_reader:
        input_rows.append(row)

    print("Begin import... ")

    # Now, insert data and generate relationships
    for irow,row in enumerate(input_rows):
        new_site = Site()
        lang_list = []
        gz_list = []

        for icol,col in enumerate(row):
            col_name = str.lower(header_row[icol]).strip()
            is_blankable_field = Site._meta.get_field(col_name).blank
            is_nullable_field = Site._meta.get_field(col_name).null
            field_default_value = Site._meta.get_field(col_name).default

            # Prevent blank fields from being interpreted as null
            if is_blankable_field and not is_nullable_field and col is None:
                col = ""
            # If field is blank, and attribute has default value, use default value
            elif (col is None or col == "" or col.isspace()) and field_default_value != NOT_PROVIDED:
                col = field_default_value

            if col_name in HEADER_NAMES:
                # If date, format to datetime object
                if col_name == 'last_checked':
                    col = parser.parse(col)
                setattr(new_site,col_name,col)

            elif col_name in M2M_HEADER_NAMES:
                items = col.split(',')

                for item in items:
                    if len(item.strip()) > 0:
                        if col_name == "language":
                            language = Language(name=item)
                            if not Language.objects.filter(name=item).exists():
                                total_count_stats["languages"] += 1
                            language.save()
                            lang_list.append(language)

                        elif col_name == "geography":
                            geo_zone = GeoZone(name=item)
                            if not GeoZone.objects.filter(name=item).exists():
                                total_count_stats["geozones"] += 1
                            geo_zone.save()
                            gz_list.append(geo_zone)

            else:
                raise CommandError("Unrecognized column name: %s" % col_name)

        # Save objects
        if Site.objects.filter(url=new_site.url).exists():
            old_version = Site.objects.filter(url=new_site.url).latest('active_start_date')
            old_version.active_end_date = new_site.active_start_date
            old_version.save()

        total_count_stats["sites"] += 1
        new_site.save()

        for lang in lang_list:
            # Insert record into junction table to associate with site
            if not SiteLanguage.objects.filter(site_id=new_site.pk, language_id=lang.name).exists():
                total_count_stats["site_languages"] += 1
                site_language = SiteLanguage(site_id=new_site.pk, language_id=lang.name)
                site_language.save()

        for gz in gz_list:
            # Insert record into junction table to associate with site
            if not SiteGeoZone.objects.filter(site_id=new_site.pk, geo_zone_id=gz.name).exists():
                total_count_stats["site_geozones"] += 1
                site_geozone = SiteGeoZone(site_id=new_site.pk, geo_zone_id=gz.name)
                site_geozone.save()

    print("Finished!")
    report_string = "\nReport:\n"
    report_string += "Number of sites imported: %s\n" % total_count_stats["sites"]
    report_string += "Number of languages imported: %s\n" % total_count_stats["languages"]
    report_string += "Number of geozones imported: %s\n" % total_count_stats["geozones"]
    report_string += "Number of site_languages created: %s\n" % total_count_stats["site_languages"]
    report_string += "Number of site_geozones created: %s\n" % total_count_stats["site_geozones"]

    return report_string

