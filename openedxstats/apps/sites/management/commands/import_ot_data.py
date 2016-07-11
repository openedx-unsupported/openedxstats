from django.core.management.base import BaseCommand, CommandError
from ...models import SiteSummarySnapshot
import csv
import sys
from dateutil import parser
from django.db.models.fields import NOT_PROVIDED

# Fields that the csv must have
REQUIRED_COLS = ["when", "sites", "courses", "reasons for discrepencies"]
# Columns to ignore
IGNORED_COLS = ["courses-per-site",]


class Command(BaseCommand):
    """
    Allows for import of over-time site and course data from a csv file to the app database.
    Example command input:  python manage.py import_ot_data test_data/over_time_data.csv
    """

    help = 'Imports Open edX over-time data from a correctly formatted csv file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Specify file to use as source for input data.')

    def handle(self, *args, **options):
        db_check()
        # Open the csv file
        with open(options['csv_file'], 'r+') as csvfile:
            result_string = import_data(csvfile)
            return result_string


def check_for_required_cols(header_row):
    """
    Checks to make sure that there are required columns in the csv file header_row and that there are not duplicate
    columns. The header_row should be the first row in the csv file
    :param header_row:
    :return:
    """
    required_cols = list(REQUIRED_COLS)
    checked_cols = []
    for col in header_row:
        col_name = str.lower(col).strip()
        if col_name in required_cols:
            required_cols.remove(col_name)
        if col_name in checked_cols:
            raise CommandError("Duplicate column detected: %s" % col_name)
        checked_cols.append(col_name)

    if len(required_cols) > 0:
        raise CommandError("Missing required cols in csv file: %s" % required_cols)
    else:
        return


def db_check():
    """
    Raise a warning prompt if there are already records in the SiteSummarySnapshot DB table.
    :return:
    """
    if SiteSummarySnapshot.objects.count() > 0:
        try:
            print("Rows already detected in SiteSummarySnapshot DB table, importing new data could/"
                  " result in errors or duplicates.")
            user_input = str(input("Continue with import? Enter 'yes' or 'no': "))
            if str.lower(user_input).strip() != "yes":
                print("Exiting...")
                sys.exit()
        except ValueError:
            print("Unrecognized input, cancelling import...")


def import_data(csvfile):
    """
    Iterates through each row of the provided csv, creating the a SiteSummarySnapshot object and saving to the DB
    :param csvfile:
    :return:
    """
    total_count_stats = {"snapshots": 0}
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
        new_snapshot = SiteSummarySnapshot()

        for icol,col in enumerate(row):
            col_name = str.lower(header_row[icol]).strip()
            if col_name in IGNORED_COLS:
                continue
            if col_name == 'when':
                col_name = 'timestamp'
            if col_name == 'sites':
                col_name = 'num_sites'
            if col_name == 'courses':
                col_name = 'num_courses'
            if col_name == 'reasons for discrepencies':
                col_name = 'notes'

            is_blankable_field = SiteSummarySnapshot._meta.get_field(col_name).blank
            is_nullable_field = SiteSummarySnapshot._meta.get_field(col_name).null
            field_default_value = SiteSummarySnapshot._meta.get_field(col_name).default

            # Prevent blank fields from being interpreted as null
            if is_blankable_field and not is_nullable_field and col is None:
                col = ""
            # If field is blank, and attribute has default value, use default value
            elif (col is None or col == "" or col.isspace()) and field_default_value != NOT_PROVIDED:
                col = field_default_value

            # If date, format to datetime object
            if col_name is 'timestamp':
                col = parser.parse(col)

            setattr(new_snapshot,col_name,col)

        # Save object
        total_count_stats["snapshots"] += 1
        new_snapshot.save()


    print("Finished!")
    report_string = "Number of snapshots imported: %s\n" % total_count_stats["snapshots"]

    return report_string
