import os.path
from django.test import TestCase
from openedxstats.apps.sites.management.commands.import_sites import import_data
from django.core.management.base import CommandError
from django.core.exceptions import FieldDoesNotExist
from django.core.management import call_command
from django.utils.six import StringIO
from django.contrib.auth.models import User
from datetime import datetime
from openedxstats.apps.sites.models import Site, GeoZone, Language, SiteGeoZone, SiteLanguage, SiteSummarySnapshot
from openedxstats.apps.sites.forms import SiteForm, GeoZoneForm, LanguageForm

BASE = os.path.dirname(os.path.abspath(__file__))


class ImportScriptTestCase(TestCase):
    """
    Tests for import_sites management command.
    """

    def test_import_date_from_correctly_formatted_file(self):
        source = os.path.join(BASE, "test_data/edx_sites_csv.csv")
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
        source = os.path.join(BASE, "test_data/wrongly_formatted_data.csv")
        with open(source, 'r+') as csvfile:
            with self.assertRaises(FieldDoesNotExist):
                import_data(csvfile)

    def test_import_data_from_minimum_req_cols_csv(self):
        source = os.path.join(BASE, "test_data/urls_only.csv")
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
        source = os.path.join(BASE, "test_data/blank.csv")
        with open(source, 'r+'):
            with self.assertRaises(CommandError):
                call_command('import_sites', source)

    def test_import_from_wrong_file_type(self):
        source = os.path.join(BASE, "test_data/text_file.txt")
        with open(source, 'r+'):
            with self.assertRaises(CommandError):
                call_command('import_sites', source)

    def test_duplicate_data(self):
        source = os.path.join(BASE, "test_data/edx_sites_csv.csv")
        additional_source = os.path.join(BASE, "test_data/edx_sites_csv_one_addition.csv")

        with open(source, 'r+'):
            call_command('import_sites', source)

        with open(additional_source, 'r+'):
            with self.assertRaises(CommandError):
                call_command('import_sites', additional_source)

    def test_import_duplicate_cols(self):
        source = os.path.join(BASE, "test_data/duplicate_cols.csv")

        with open(source, 'r+'):
            with self.assertRaises(CommandError):
                call_command('import_sites', source)

    def test_import_duplicate_date_cols(self):
        source = os.path.join(BASE, "test_data/duplicate_date_cols.csv")

        with open(source, 'r+'):
            with self.assertRaises(CommandError):
                call_command('import_sites', source)

    def test_import_newer_version(self):
        source = os.path.join(BASE, "test_data/edx_sites_csv.csv")
        additional_source = os.path.join(BASE, "test_data/one_updated_site.csv")

        with open(source, 'r+'):
            call_command('import_sites', source)

        with open(additional_source, 'r+'):
            call_command('import_sites', additional_source)
            updated_site = Site.objects.filter(url='https://lagunita.stanford.edu').latest('active_start_date')
            self.assertEqual(updated_site.active_start_date, datetime(2016, 3, 26, 0, 0))
            self.assertEqual(Site.objects.filter(url='https://lagunita.stanford.edu').count(), 2)
            self.assertEqual(Site.objects.count(), 269)


class ImportOTDataTestCase(TestCase):
    """
    Tests for the import ot_data management command.
    """

    def test_import_from_correctly_formatted_file(self):
        source = os.path.join(BASE, "test_data/over_time_data.csv")

        with open(source, 'r+'):
            call_command('import_ot_data', source)
            self.assertEqual(SiteSummarySnapshot.objects.count(), 93)


    def test_import_wrong_cols(self):
        pass

    def test_db_check(self):
        source = os.path.join(BASE, "test_data/over_time_data.csv")

        with open(source, 'r+'):
            call_command('import_ot_data', source)




class SubmitSiteFormTestCase(TestCase):
    """
    Tests for the add site form.
    """

    def setUp(self):
        user = User.objects.create_user('testuser', 'testuser@edx.com', 'password')
        if user is None:
            self.fail("Could not create testuser in setUp()")
        self.client.login(username='testuser', password='password')

    def test_form_validation_for_blank_url(self):
        form = SiteForm(data={'url': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['url'], ['This field is required']
        )

    def test_form_validation_for_existing_url(self):
        new_site = Site(url='https://lagunitas.stanford.edu', active_start_date='2016-10-10')
        new_site.save()
        form_data = {'url': 'https://lagunitas.stanford.edu', 'active_start_date': '2016-10-10'}
        form = SiteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], ["Site with this Url and Active start date already exists."])

        # Will give an error message
        response = self.client.post('/sites/add_site/', form_data, follow=True)
        self.assertEqual(Site.objects.count(), 1)
        storage = response.context['messages']
        self.assertEqual(len(storage), 1)
        self.assertIn("Site with this Url and Active start date already exists.", list(storage)[0].message)

    def test_add_a_new_version(self):
        new_site = Site(url='https://test.com', active_start_date='2016-10-10 15:55', course_type='SPOC')
        new_site.save()
        form_data = {
            'site_type': 'TEST',
            'url': 'https://test.com',
            'active_start_date': '2016-10-10 16:30',
            'course_type': 'Both'
        }
        form = SiteForm(data=form_data)
        self.assertTrue(form.is_valid())

        self.client.post('/sites/add_site/', form_data)

        updated_site = Site.objects.filter(url='https://test.com').order_by('-active_start_date').first()
        old_site = Site.objects.filter(url='https://test.com').order_by('-active_start_date').last()
        self.assertEqual(Site.objects.count(), 2)
        self.assertEqual(Site.objects.filter(url='https://test.com').count(), 2)
        self.assertEqual(updated_site.course_type, 'Both')
        self.assertEqual(old_site.active_end_date, datetime(2016, 10, 10, 16, 30))
        self.assertIsNone(updated_site.active_end_date)

    def test_add_an_old_version(self):
        new_site = Site(url='https://test.com', active_start_date='2016-10-10 16:30', course_type='SPOC')
        new_site.save()
        form_data = {
            'site_type': 'TEST',
            'url': 'https://test.com',
            'active_start_date': '2016-10-10 14:30',
            'course_type': 'Both'
        }
        form = SiteForm(data=form_data)
        self.assertTrue(form.is_valid())

        self.client.post('/sites/add_site/', form_data)

        updated_site = Site.objects.filter(url='https://test.com').order_by('-active_start_date').first()
        old_site = Site.objects.filter(url='https://test.com').order_by('-active_start_date').last()
        self.assertEqual(Site.objects.count(), 2)
        self.assertEqual(Site.objects.filter(url='https://test.com').count(), 2)
        self.assertEqual(updated_site.course_type, 'SPOC')
        self.assertEqual(old_site.active_start_date, datetime(2016, 10, 10, 14, 30))
        self.assertEqual(old_site.active_end_date, datetime(2016, 10, 10, 16, 30))
        self.assertIsNone(updated_site.active_end_date)

    def test_add_a_single_site_with_required_fields(self):
        form_data = {
            'site_type': 'General',
            'name': 'Test',
            'url': 'https://convolutedurl.biz',
            'course_type': 'Unknown',
            'active_start_date': '2016-10-10',
        }

        self.assertEqual(0, Site.objects.count())

        response = self.client.post('/sites/add_site/', form_data)

        self.assertEqual(1, Site.objects.count())
        saved_site = Site.objects.first()
        self.assertEqual(saved_site.url, form_data['url'])

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/sites/all/')

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
            'org_type': 'Academic',
            'language': ('English', 'Chinese'),
            'geography': ('Greece', '\u00e9'),
            'github_fork': 'Estranged-Spork',
            'notes': 'What a day it is to be alive.',
            'course_type': 'Unknown',
            'registered_user_count': '3333',
            'active_learner_count': '1111',
            'active_start_date': '2016-03-24',
        }

        self.assertEqual(0, Site.objects.count())

        response = self.client.post('/sites/add_site/', form_data)

        self.assertEqual(1, Site.objects.count())
        saved_site = Site.objects.first()
        self.assertEqual(saved_site.site_type, form_data['site_type'])
        self.assertEqual(saved_site.name, form_data['name'])
        self.assertEqual(saved_site.url, form_data['url'])
        self.assertEqual(saved_site.course_count, 1337)
        self.assertEqual(saved_site.active_start_date, datetime(2016, 3, 24, 0, 0))
        self.assertCountEqual(saved_site.language.all(), [lang1, lang2])
        self.assertCountEqual(saved_site.geography.all(), [geozone1, geozone2])
        self.assertEqual(saved_site.course_type, form_data['course_type'])

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/sites/all/')

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
        self.assertEqual(response['location'], '/sites/all/')

    def test_add_language_that_already_exists(self):
        new_language = Language(name='κόσμε')
        new_language.save()
        form = LanguageForm(data={'name': 'κόσμε'})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['name'], ['Language with this Name already exists.']
        )

        # Will give an error message
        response = self.client.post('/sites/add_language/', {'name': 'κόσμε'}, follow=True)
        self.assertEqual(Language.objects.count(), 1)
        storage = response.context['messages']
        self.assertEqual(len(storage), 1)
        self.assertIn("Language with this Name already exists.", list(storage)[0].message)

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
        self.assertEqual(response['location'], '/sites/all/')

    def test_add_geozone_that_already_exists(self):
        new_geozone = GeoZone(name='ANewGeozone')
        new_geozone.save()
        form = GeoZoneForm(data={'name': 'ANewGeozone'})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['name'], ['Geo zone with this Name already exists.']
        )

        # Will give an error message
        response = self.client.post('/sites/add_geozone/', {'name': 'ANewGeozone'}, follow=True)
        self.assertEqual(GeoZone.objects.count(), 1)
        storage = response.context['messages']
        self.assertEqual(len(storage), 1)
        self.assertIn("Geo zone with this Name already exists.", list(storage)[0].message)

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

    # TODO: Consider adding an update tab to "Add a site" so that you can populate form with existing data to easily update


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
        self.assertEqual(str(new_site), " --- ")
        self.assertEqual(str(sitelang2), "---lang2")

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
        self.assertEqual(str(sitegeozone1), "https://www.κόσμε.co---Greece")
        self.assertEqual(str(geozone2), "\u00e9")

