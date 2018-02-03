import os.path
from django.test import TestCase
from openedxstats.apps.sites.management.commands.import_sites import import_data
from django.core.management.base import CommandError
from django.core.exceptions import FieldDoesNotExist
from django.core.management import call_command
from django.utils.six import StringIO
from django.contrib.auth.models import User
from datetime import datetime, date, timedelta
import json
from openedxstats.apps.sites.models import Site, GeoZone, Language, SiteGeoZone, SiteLanguage, SiteSummarySnapshot, \
    FilenameLog, AccessLogAggregate
from openedxstats.apps.sites.forms import SiteForm, GeoZoneForm, LanguageForm
from django.core.serializers import serialize
from openedxstats.apps.sites.views import OTChartView
import boto
from boto.s3.bucket import Bucket, Key
from openedxstats.apps.sites.management.commands import fetch_referrer_logs

BASE = os.path.dirname(os.path.abspath(__file__))


class ImportScriptTestCase(TestCase):
    """
    Tests for import_sites management command.
    """

    def test_import_data_from_correctly_formatted_file(self):
        source = os.path.join(BASE, "test_data/test_sites.csv")
        expected_output = ("Report:\n"
                           "Number of sites imported: 5\n"
                           "Number of languages imported: 3\n"
                           "Number of geozones imported: 2\n"
                           "Number of site_languages created: 3\n"
                           "Number of site_geozones created: 4\n")
        out = StringIO()
        call_command('import_sites', source, stdout=out)
        self.assertIn(expected_output, out.getvalue())

    def test_import_wrongly_formatted_data_from_file(self):
        source = os.path.join(BASE, "test_data/wrongly_formatted_data.csv")
        with open(source) as csvfile:
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
        call_command('import_sites', source, stdout=out)
        self.assertIn(expected_output, out.getvalue())

    def test_import_from_blank_csv_file(self):
        source = os.path.join(BASE, "test_data/blank.csv")
        with self.assertRaises(CommandError):
            call_command('import_sites', source)

    def test_import_from_wrong_file_type(self):
        source = os.path.join(BASE, "test_data/text_file.txt")
        with self.assertRaises(CommandError):
            call_command('import_sites', source)

    def test_duplicate_data(self):
        source = os.path.join(BASE, "test_data/test_sites.csv")
        additional_source = os.path.join(BASE, "test_data/test_sites_one_addition.csv")

        call_command('import_sites', source)
        with self.assertRaises(CommandError):
            call_command('import_sites', additional_source)

    def test_import_duplicate_cols(self):
        source = os.path.join(BASE, "test_data/duplicate_cols.csv")
        with self.assertRaises(CommandError):
            call_command('import_sites', source)

    def test_import_duplicate_date_cols(self):
        source = os.path.join(BASE, "test_data/duplicate_date_cols.csv")
        with self.assertRaises(CommandError):
            call_command('import_sites', source)

    def test_import_newer_version(self):
        source = os.path.join(BASE, "test_data/test_sites.csv")
        additional_source = os.path.join(BASE, "test_data/one_updated_site.csv")
        call_command('import_sites', source)

        call_command('import_sites', additional_source)
        updated_site = Site.objects.filter(url='https://test3.com').latest('active_start_date')
        self.assertEqual(updated_site.active_start_date, datetime(2016, 4, 15, 0, 0))
        self.assertEqual(Site.objects.filter(url='https://test3.com').count(), 2)
        self.assertEqual(Site.objects.count(), 6)


class ImportOTDataTestCase(TestCase):
    """
    Tests for the import ot_data management command.
    """

    def test_import_from_correctly_formatted_file(self):
        source = os.path.join(BASE, "test_data/over_time_data.csv")

        call_command('import_ot_data', source)
        self.assertEqual(SiteSummarySnapshot.objects.count(), 3)


class SubmitSiteFormTestCase(TestCase):
    """
    Tests for the add site form.
    """

    def setUp(self):
        User.objects.create_user('testuser', 'testuser@edx.com', 'password')
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


class ModelsTestCase(TestCase):
    """
    Tests for models.
    """

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


class OTChartTestCase(TestCase):
    """
    Tests for the OT Chart.
    """

    def setUp(self):
        User.objects.create_user('testuser', 'testuser@edx.com', 'password')
        self.client.login(username='testuser', password='password')

    def test_nothing_imported_from_ajax_call(self):
        # Ajax request
        response = self.client.post('/sites/ot_chart/', context_type='application/json',
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), json.dumps([]))

    def test_json_data_returned_after_ajax_call(self):
        snapshot_list = []
        snapshot = SiteSummarySnapshot(
            timestamp=datetime(2016, 7, 1, 0, 0, 0),
            num_sites=100,
            num_courses=1000,
            notes="test"
        )
        snapshot_list.append(snapshot)
        snapshot.save()
        for date in OTChartView.daterange(OTChartView(), snapshot.timestamp, datetime.now() + timedelta(days=1)):
            empty_snapshot = SiteSummarySnapshot(
                timestamp=date,
                num_sites=0,
                num_courses=None,
                notes="Auto-generated day summary"
            )
            snapshot_list.append(empty_snapshot)

        # Ajax request
        response = self.client.post('/sites/ot_chart/', context_type='application/json',
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        expected_json = json.loads(serialize('json', [snapshot]))
        response_json = json.loads(response.content.decode())

        for i, item in enumerate(expected_json):
            self.assertEqual(expected_json[i], response_json[i])


class UpdateSiteTestCase(TestCase):
    """
    Tests for updating a site.
    """

    def setUp(self):
        User.objects.create_user('testuser', 'testuser@edx.com', 'password')
        self.client.login(username='testuser', password='password')

    def test_updating_with_no_changes(self):
        new_site = Site(name='TEST', url='https://test.com', active_start_date=datetime(2015, 10, 10, 15, 55),
                        course_type='SPOC', site_type='General')
        new_site.save()
        form_data = {
            'name': 'TEST',
            'site_type': 'General',
            'url': 'https://test.com',
            'active_start_date': datetime.now(),
            'course_type': 'SPOC'
        }
        form = SiteForm(data=form_data)
        self.assertTrue(form.is_valid())

        self.assertEqual(Site.objects.count(), 1)
        self.client.post('/sites/update_site/'+str(new_site.pk)+'/', form_data)

        updated_site = Site.objects.filter(url='https://test.com').order_by('-active_start_date').first()
        old_site = Site.objects.filter(url='https://test.com').order_by('-active_start_date').last()
        self.assertEqual(Site.objects.count(), 2)
        self.assertEqual(Site.objects.filter(url='https://test.com').count(), 2)
        self.assertEqual(updated_site.course_type, old_site.course_type)
        self.assertGreater(updated_site.active_start_date, old_site.active_start_date)
        self.assertEqual(updated_site.active_start_date, old_site.active_end_date)
        self.assertIsNone(updated_site.active_end_date)

    def test_updating_with_valid_changes(self):
        new_site = Site(name='TEST', url='https://test.com', active_start_date=datetime(2015, 10, 10, 15, 55),
                        course_type='SPOC', site_type='General')
        new_site.save()
        form_data = {
            'name': 'TEST2',
            'site_type': 'General',
            'url': 'https://test.com',
            'active_start_date': datetime.now(),
            'course_type': 'MOOC',
            'active_learner_count': 50,
            'notes': 'Some basic changes'
        }
        form = SiteForm(data=form_data)
        self.assertTrue(form.is_valid())

        self.assertEqual(Site.objects.count(), 1)
        self.client.post('/sites/update_site/'+str(new_site.pk)+'/', form_data)

        updated_site = Site.objects.filter(url='https://test.com').order_by('-active_start_date').first()
        old_site = Site.objects.filter(url='https://test.com').order_by('-active_start_date').last()
        self.assertEqual(Site.objects.count(), 2)
        self.assertEqual(Site.objects.filter(url='https://test.com').count(), 2)
        self.assertEqual(updated_site.course_type, 'MOOC')
        self.assertEqual(updated_site.notes, 'Some basic changes')
        self.assertEqual(old_site.notes, '')
        self.assertGreater(updated_site.active_start_date, old_site.active_start_date)
        self.assertEqual(updated_site.active_start_date, old_site.active_end_date)
        self.assertIsNone(updated_site.active_end_date)

    def test_updating_to_same_active_start_date(self):
        new_site = Site(name='TEST', url='https://test.com', active_start_date='2015-10-10',
                        course_type='SPOC', site_type='General')
        new_site.save()
        form_data = {
            'name': 'TEST',
            'site_type': 'General',
            'url': 'https://test.com',
            'active_start_date': '2015-10-10',
            'course_type': 'SPOC'
        }
        form = SiteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], ["Site with this Url and Active start date already exists."])
        # Will give an error message
        response = self.client.post('/sites/update_site/'+str(new_site.pk)+'/', form_data, follow=True)
        self.assertEqual(Site.objects.count(), 1)
        storage = response.context['messages']
        self.assertEqual(len(storage), 1)
        self.assertIn("Site with this Url and Active start date already exists.", list(storage)[0].message)

    def test_updating_non_current_version(self):
        outdated_site = Site(name='TEST', url='https://test.com', active_start_date='2015-10-10',
                             active_end_date='2015-11-11', course_type='SPOC', site_type='General')
        outdated_site.save()
        form_data = {
            'name': 'TEST',
            'site_type': 'General',
            'url': 'https://test.com',
            'active_start_date': '2015-10-10',
            'course_type': 'SPOC'
        }
        # Will give an error message
        response = self.client.post('/sites/update_site/' + str(outdated_site.pk) + '/', form_data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Site.objects.count(), 1)
        self.assertEqual(Site.objects.get(url='https://test.com'), outdated_site)

    def test_navigating_to_update_page_for_non_current_version(self):
        outdated_site = Site(name='TEST', url='https://test.com', active_start_date='2015-10-10',
                             active_end_date='2015-11-11', course_type='SPOC', site_type='General')
        outdated_site.save()
        response = self.client.get('/sites/update_site/'+str(outdated_site.pk)+'/')
        self.assertEqual(Site.objects.count(), 1)
        self.assertEqual(response.status_code, 403)

    def test_navigating_to_update_page_for_nonexistent_version(self):
        response = self.client.get('/sites/update_site/999999999/')
        self.assertEqual(Site.objects.count(), 0)
        self.assertEqual(response.status_code, 404)


class ReferrerLogTestCase(TestCase):
    """
    Tests for fetch_referrer_logs management script.
    THESE TESTS WILL NOT RUN UNLESS YOU HAVE BEEN GIVEN VALID AWS CREDENTIALS FOR EDX!!!
    If you don't want to run these tests because you do not have the key, you should comment out this class.
    """

    def setUp(self):
        self.conn = boto.connect_s3()

    def test_can_connect_to_s3(self):
        bucket = self.conn.get_bucket("edx-s3-logs", validate=False)
        self.assertIsInstance(bucket, Bucket)

    def test_can_download_keys(self):
        bucket = self.conn.get_bucket("edx-s3-logs", validate=False)
        # Get only today's keys to reduce search time
        accessible_keys = fetch_referrer_logs.get_accessible_keys(
            bucket,
            "edx-static-cloudfront/E32IHGJJSQ4SLL." + date.today().strftime('%Y-%m-%d')
        )
        self.assertIsNotNone(accessible_keys)
        self.assertIsInstance(accessible_keys[0], Key)

    def test_can_unzip_one_file(self):
        bucket = self.conn.get_bucket("edx-s3-logs", validate=False)
        # Get only today's keys to reduce search time
        accessible_keys = fetch_referrer_logs.get_accessible_keys(
            bucket,
            "edx-static-cloudfront/E32IHGJJSQ4SLL." + date.today().strftime('%Y-%m-%d')
        )

        num_files_processed = fetch_referrer_logs.process_keys([accessible_keys[0],])
        self.assertEqual(num_files_processed, 1)
        self.assertEqual(FilenameLog.objects.all().count(), 1)
        self.assertIsNotNone(AccessLogAggregate.objects.all())

    # Reduce number of files processed to reduce test time
    def test_todays_logs(self):
        bucket = self.conn.get_bucket("edx-s3-logs", validate=False)
        # Get only today's keys to reduce search time
        accessible_keys = fetch_referrer_logs.get_accessible_keys(
            bucket,
            "edx-static-cloudfront/E32IHGJJSQ4SLL." + date.today().strftime('%Y-%m-%d')
        )

        # Process only first 10 files to save time
        num_files_processed = fetch_referrer_logs.process_keys(accessible_keys[:10])
        self.assertEqual(num_files_processed, 10)
        self.assertEqual(FilenameLog.objects.all().count(), 10)
        self.assertIsNotNone(AccessLogAggregate.objects.all())

    def test_no_duplicate_files_are_processed(self):
        bucket = self.conn.get_bucket("edx-s3-logs", validate=False)
        # Get only today's keys to reduce search time
        accessible_keys = fetch_referrer_logs.get_accessible_keys(
            bucket,
            "edx-static-cloudfront/E32IHGJJSQ4SLL." + date.today().strftime('%Y-%m-%d')
        )

        num_files_processed = fetch_referrer_logs.process_keys(accessible_keys[:3])
        self.assertEqual(num_files_processed, 3)
        self.assertEqual(FilenameLog.objects.all().count(), 3)
        self.assertIsNotNone(AccessLogAggregate.objects.all())

        # Now input those 3 files again with an extra, only the extra should be processed
        num_files_processed = fetch_referrer_logs.process_keys(accessible_keys[:4])
        self.assertEqual(num_files_processed, 1)
        self.assertEqual(FilenameLog.objects.all().count(), 4)
