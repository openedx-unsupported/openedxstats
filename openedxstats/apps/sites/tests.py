from django.test import TestCase
from management.commands.import_sites import import_data, check_for_required_cols
from django.core.management.base import CommandError
from django.core.exceptions import FieldDoesNotExist
from django.core.management import call_command
from django.utils.six import StringIO


class ImportScriptTestCase(TestCase):
    """
    Tests for import_sites management command.
    """

    def test_import_date_from_correctly_formatted_file(self):
        source = "/Users/zacharyrobbins/Documents/postgres_data/edx_sites_csv.csv"
        expected_output = ("Report:\n"
                           "Number of sites imported: 268\n"
                           "Number of languages imported: 35\n"
                           "Number of geozones imported: 59\n"
                           "Number of site_languages created: 268\n"
                           "Number of site_geozones created: 268\n")
        out = StringIO()
        with open(source, 'rwb'):
            call_command('import_sites', source, stdout = out)
            self.assertIn(expected_output, out.getvalue())


    def test_import_wrongly_formatted_data_from_file(self):
        source = "/Users/zacharyrobbins/Documents/postgres_data/wrongly_formatted_data.csv"
        with open(source, 'rwb') as csvfile:
            with self.assertRaises(FieldDoesNotExist):
                import_data(csvfile)  # Import data

    def test_import_data_from_minimum_req_cols_csv(self):
        source = "/Users/zacharyrobbins/Documents/postgres_data/urls_only.csv"
        expected_output = ("Report:\n"
                           "Number of sites imported: 3\n"
                           "Number of languages imported: 0\n"
                           "Number of geozones imported: 0\n"
                           "Number of site_languages created: 0\n"
                           "Number of site_geozones created: 0\n")
        out = StringIO()
        with open(source, 'rwb'):
            call_command('import_sites', source, stdout=out)
            self.assertIn(expected_output, out.getvalue())

    def test_import_from_blank_csv_file(self):
        source = "/Users/zacharyrobbins/Documents/postgres_data/blank.csv"
        with open(source, 'rwb'):
            with self.assertRaises(CommandError):
                call_command('import_sites', source)

    def test_import_from_wrong_file_type(self):
        source = "/Users/zacharyrobbins/Documents/postgres_data/text_file.txt"
        with open(source, 'rwb'):
            with self.assertRaises(CommandError):
                call_command('import_sites', source)

    def test_check_for_idempotency(self):
        source = "/Users/zacharyrobbins/Documents/postgres_data/edx_sites_csv.csv"
        additional_source = "/Users/zacharyrobbins/Documents/postgres_data/edx_sites_csv_one_addition.csv"
        expected_output = ("Report:\n"
                           "Number of sites imported: 1\n"
                           "Number of languages imported: 0\n"
                           "Number of geozones imported: 2\n"
                           "Number of site_languages created: 1\n"
                           "Number of site_geozones created: 2\n")
        out = StringIO()
        with open(source, 'rwb'):
            call_command('import_sites', source)

        with open(additional_source, 'rwb'):
            call_command('import_sites', additional_source, stdout=out)
            self.assertIn(expected_output, out.getvalue())