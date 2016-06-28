from django.core.management.base import BaseCommand, CommandError
from ...models import *
import csv
from dateutil import parser
from django.db.models.fields import NOT_PROVIDED

# Fields that the csv must have
REQUIRED_COLS = ["url"]
# Fields that we allow to be imported from the csv
HEADER_NAMES = ["site_type", "name", "url", "course_count", "last_checked", "org_type", "github_fork", "notes",
                "course_type", "registered_user_count", "active_learner_count", "active_start_date", "active_end_date"]
# Fields that represent m2m relationships (and may have more than one value)
M2M_HEADER_NAMES = ["geography", "language"]


class Command(BaseCommand):
    """
    Allows for import of site data from a csv file to the app database.
    Example command input:  python manage.py import_sites test_data/edx_sites_csv.csv

    *****
    The Open edX Sites list current as of June 2016 is already correctly formatted in test_data/edx_sites_csv.csv
    *****

    IMPORTANT NOTES:
    - The csv file's first row MUST be a header row, with all of the column names
    - All rows following the header row should be data that conforms to the columns discovered in the header row
    - The CSV file must at least have the cols in REQUIRED_COLS
    - Data under last_checked or active_start_date must be in a valid date or datetime format, or the parser will raise
      an error
    - If no value is provided for site_type, course_type, or active_start_date, they will default to values of
      'General', 'Unknown', and the current datetime, respectively.
    """

    help = 'Imports Open edX site data from a correctly formatted csv file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Specify file to use as source for input data.')

    def handle(self, *args, **options):
        # Open the csv file
        with open(options['csv_file'], 'r+') as csvfile:
            result_string = import_data(csvfile)
            return result_string


def check_for_required_cols(header_row):
    """
    Checks to make sure that there are required columns in the csv file header_row and that there are not duplicate
    columns. Also checks that there is only one of either 'last_checked' or 'active_start_date'
    (since they are referencing the same thing)
    The header_row should be the first row in the csv file
    :param header_row:
    :return:
    """
    required_cols = list(REQUIRED_COLS)
    checked_cols = []
    for col in header_row:
        if col in required_cols:
            required_cols.remove(col)
        if col in checked_cols:
            raise CommandError("Duplicate column detected: %s" % col)
        if (col == 'last_checked' and 'active_start_date' in checked_cols)\
                or (col == 'active_start_date' and 'last_checked' in checked_cols):
            raise CommandError("Can't have both a 'last_checked' and 'active_start_date' column!")
        checked_cols.append(col)

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
            if col_name == 'last_checked':
                col_name = 'active_start_date'
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
                if col_name in ['active_start_date', 'active_end_date']:
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

        # Save objects
        # Check if an old version exists
        if Site.objects.filter(url=new_site.url).exists():
            old_version = Site.objects.filter(url=new_site.url).latest('active_start_date')
            if old_version.active_start_date == new_site.active_start_date:
                raise CommandError(
                    "Cannot insert duplicate records. Key (url, active_start_date)=(%s, %s) already exists." % (
                    new_site.url, new_site.active_start_date))
            else:
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
