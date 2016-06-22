from django.test import TestCase
from .management.commands.import_sites import import_data, check_for_required_cols
from django.core.management.base import CommandError
from django.core.exceptions import FieldDoesNotExist
from django.core.management import call_command
from django.utils.six import StringIO
from .models import Site, GeoZone, Language, SiteGeoZone, SiteLanguage
from .forms import SiteForm, GeoZoneForm, LanguageForm


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
            call_command('import_sites', source, stdout=out)
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
        form = SiteForm(data={'url': ''})
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
        lang1 = Language(name="English")
        lang2 = Language(name="Chinese")
        lang1.save()
        lang2.save()
        geozone1 = GeoZone(name="Greece")
        geozone2 = GeoZone(name="\u00e9")
        geozone1.save()
        geozone2.save()

        form_data = {
            'site_type': 'General',
            'name': 'κόσμε',
            'url': 'https://convolutedurl.biz',
            'course_count': '1337',
            'last_checked': '2016-03-24',
            'org_type': 'Academic',
            'language': ('English', 'Chinese'),
            'geography': ('Greece', '\u00e9'),
            'github_fork': 'Estranged-Spork',
            'notes': 'What a day it is to be alive.',
            'course_type': 'Unknown',
            'registered_user_count': '3333',
            'active_learner_count': '1111',
        }

        self.assertEqual(0, Site.objects.count())

        response = self.client.post('/sites/add_site/', form_data)

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
        new_language = Language(name='κόσμε')
        new_language.save()
        form = LanguageForm(data={'name': 'κόσμε'})
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


class ModelsTestCase(TestCase):
    def test_site_get_languages_method(self):
        new_site = Site()
        new_site.save()
        lang1 = Language(name="lang1")
        lang2 = Language(name="lang2")
        lang1.save()
        lang2.save()
        sitelang1 = SiteLanguage(site_id=new_site.pk, language_id=lang1.pk)
        sitelang2 = SiteLanguage(site_id=new_site.pk, language_id=lang2.pk)

        sitelang1.save()
        sitelang2.save()

        # Renamed from assertItemsEqual in python 2
        self.assertCountEqual(new_site.get_languages(), "lang1, lang2")
        self.assertEqual(new_site.__str__(), " --- ")
        self.assertEqual(sitelang2.__str__(), "---lang2")

    def test_site_get_geographies_method_with_unicode(self):
        new_site = Site()
        new_site.url = "https://www.κόσμε.co"
        new_site.save()
        geozone1 = GeoZone(name="Greece")
        geozone2 = GeoZone(name="\u00e9")
        geozone1.save()
        geozone2.save()
        sitegeozone1 = SiteGeoZone(site_id=new_site.pk, geo_zone_id=geozone1.pk)
        sitegeozone2 = SiteGeoZone(site_id=new_site.pk, geo_zone_id=geozone2.pk)

        sitegeozone1.save()
        sitegeozone2.save()

        # Renamed from assertItemsEqual in python 2
        self.assertCountEqual(new_site.get_geographies(), "Greece, \u00e9")
        self.assertEqual(sitegeozone1.__str__(), "https://www.κόσμε.co---Greece")
        self.assertEqual(geozone2.__str__(), "\u00e9")

