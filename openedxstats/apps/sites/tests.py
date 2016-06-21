from __future__ import unicode_literals

from django.test import TestCase
from .management.commands.import_sites import import_data
#from management.commands.import_sites import import_data, check_for_required_cols
from django.core.management.base import CommandError
from django.core.exceptions import FieldDoesNotExist
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.utils.datastructures import MultiValueDict
from django.utils.http import urlencode
from django.utils.six import StringIO
from django.http import HttpRequest
from .models import Site, GeoZone, Language
from .forms import SiteForm, GeoZoneForm, LanguageForm
from .views import add_site


class ImportScriptTestCase(TestCase):
    """
    Tests for import_sites management command.
    """

    def test_import_date_from_correctly_formatted_file(self):
        source = "/Users/zacharyrobbins/Documents/postgres_data/edx_sites_csv.csv"
        expected_output = ("Report:\n"
                           "Number of sites imported: 268\n"
                           "Number of languages imported: 34\n"
                           "Number of geozones imported: 58\n"
                           "Number of site_languages created: 271\n"
                           "Number of site_geozones created: 198\n")
        out = StringIO()
        with open(source, 'r+'):
            call_command('import_sites', source, stdout = out)
            self.assertIn(expected_output, out.getvalue())


    def test_import_wrongly_formatted_data_from_file(self):
        source = "/Users/zacharyrobbins/Documents/postgres_data/wrongly_formatted_data.csv"
        with open(source, 'r+') as csvfile:
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
        with open(source, 'r+'):
            call_command('import_sites', source, stdout=out)
            self.assertIn(expected_output, out.getvalue())

    def test_import_from_blank_csv_file(self):
        source = "/Users/zacharyrobbins/Documents/postgres_data/blank.csv"
        with open(source, 'r+'):
            with self.assertRaises(CommandError):
                call_command('import_sites', source)

    def test_import_from_wrong_file_type(self):
        source = "/Users/zacharyrobbins/Documents/postgres_data/text_file.txt"
        with open(source, 'r+'):
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
        with open(source, 'r+'):
            call_command('import_sites', source)

        with open(additional_source, 'r+'):
            call_command('import_sites', additional_source, stdout=out)
            self.assertIn(expected_output, out.getvalue())


class SubmitSiteFormTestCase(TestCase):
    """
    Tests for the add site form.
    """

    def test_form_validation_for_blank_url(self):
        form = SiteForm(data={'url':''})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['url'], ['This field is required']
        )

    def test_form_validation_for_existing_url(self):
        new_site = Site(url='https://lagunitas.stanford.edu')
        new_site.save()
        form = SiteForm(data={'url': 'https://lagunitas.stanford.edu'})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['url'], ['Site with this Url already exists.']
        )


    def test_add_a_single_site_with_required_fields(self):
        form_data = {
            'site_type': 'General',
            'name': 'Test',
            'url': 'https://convolutedurl.biz',
            'course_type': 'Unknown',
        }

        self.assertEqual(0, Site.objects.count())

        response = self.client.post('/sites/add_site/', form_data)

        self.assertEqual(1, Site.objects.count())
        saved_site = Site.objects.first()
        self.assertEqual(saved_site.url, form_data['url'])

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/sites/all')


    def test_add_a_single_site_with_all_fields(self):
        form_data = {
            'site_type': 'General',
            'name': 'Test',
            'url': 'https://convolutedurl.biz',
            'course_count': '1337',
            'last_checked': '2016-03-24',
            'org_type': 'Academic',
            #'language': ['English', 'Chinese'],
            #'geography': ['US', 'China'],
            'github_fork': 'Estranged-Spork',
            'notes': 'What a day it is to be alive.',
            'course_type': 'Unknown',
            'registered_user_count': '3333',
            'active_learner_count': '1111',
        }

        self.assertEqual(0, Site.objects.count())

        response = self.client.post('/sites/add_site/', form_data)
        # Need to urlencode in order to pass languages and geographies
        #response = self.client.post('/sites/add_site/',
        #                       urlencode(MultiValueDict(form_data), doseq=True),
        #                       content_type='application/x-www-form-urlencoded')

        self.assertEqual(1, Site.objects.count())
        saved_site = Site.objects.first()
        self.assertEqual(saved_site.url, form_data['url'])

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/sites/all')


    def test_add_language(self):
        form_data = {
            'name': 'ANewLanguage',
        }

        self.assertEqual(0, Language.objects.count())
        response = self.client.post('/sites/add_language/', form_data)

        self.assertEqual(1, Language.objects.count())
        saved_language = Language.objects.first()
        self.assertEqual(saved_language.name, form_data['name'])

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/sites/all')


    def test_add_language_that_already_exists(self):
        new_language = Language(name='ANewLanguage')
        new_language.save()
        form = LanguageForm(data={'name': 'ANewLanguage'})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['name'], ['Language with this Name already exists.']
        )


    def test_add_geozone(self):
        form_data = {
            'name': 'ANewGeozone',
        }

        self.assertEqual(0, GeoZone.objects.count())
        response = self.client.post('/sites/add_geozone/', form_data)

        self.assertEqual(1, GeoZone.objects.count())
        saved_geozone = GeoZone.objects.first()
        self.assertEqual(saved_geozone.name, form_data['name'])

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/sites/all')


    def test_add_geozone_that_already_exists(self):
        new_geozone = GeoZone(name='ANewGeozone')
        new_geozone.save()
        form = GeoZoneForm(data={'name': 'ANewGeozone'})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['name'], ['Geo zone with this Name already exists.']
        )


    def test_get_blank_site_form(self):
        response = self.client.get('/sites/add_site/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, Site.objects.count())


    def test_get_blank_language_form(self):
        response = self.client.get('/sites/add_language/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, Language.objects.count())


    def test_get_blank_geozone_form(self):
        response = self.client.get('/sites/add_geozone/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, GeoZone.objects.count())

