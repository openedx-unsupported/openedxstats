from datetime import datetime

from django.db import models
from django.contrib.postgres.fields import ArrayField

COURSE_TYPE_CHOICES = (
    ('MOOC', 'MOOC'),
    ('SPOC', 'SPOC'),
    ('Both', 'Both'),
    ('Unknown', 'Unknown'),
)

# Models

class GeoZone(models.Model):
    """
    A model describing a geographical zone.
    """
    name = models.CharField(primary_key=True, max_length=255)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Language(models.Model):
    """
    A model describing a language.
    """
    name = models.CharField(primary_key=True, max_length=255)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class OverCount(models.Model):
    """
    Record how many duplicate courses were over-counted, world-wide.
    """

    course_count = models.IntegerField()
    active_start_date = models.DateTimeField(default=datetime.now, unique=True)
    active_end_date = models.DateTimeField(null=True)

    @classmethod
    def set_latest(cls, over_count):
        """A simple way to set the current count to `over_count`."""

        # Find the latest one, set its end_date to now
        now = datetime.now()
        try:
            latest = cls.objects.get(active_end_date=None)
        except cls.DoesNotExist:
            # I guess this is the first...?
            pass
        else:
            latest.active_end_date = now
            latest.save()

        new = cls.objects.create(active_start_date=now, course_count=over_count)
        new.save()



class Site(models.Model):
    """
    A model describing an open edX website.
    """

    # Don't use null=true for CharFields as the Django default for null text is an empty string
    # Many of the sites do not have all of these fields, which is why many can be left blank

    # id <-- Automatic surrogate serial primary key created by django
    site_type = models.CharField(max_length=255, default='General')
    name = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=255)
    is_private_instance = models.BooleanField(default=False)
    is_gone = models.BooleanField(default=False)
    course_count = models.IntegerField(blank=True, null=True)
    active_start_date = models.DateTimeField(default=datetime.now)
    active_end_date = models.DateTimeField(null=True)
    org_type = models.CharField(max_length=255, blank=True)
    language = models.ManyToManyField(Language, through='SiteLanguage', blank=True)
    geography = models.ManyToManyField(GeoZone, through='SiteGeoZone', blank=True)
    github_fork = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    course_type = models.CharField(max_length=10, choices=COURSE_TYPE_CHOICES, default='Unknown')
    registered_user_count = models.IntegerField(blank=True, null=True)
    active_learner_count = models.IntegerField(blank=True, null=True)
    aliases = ArrayField(models.CharField(max_length=255), default=list, blank=True)

    def __str__(self):
        return self.name + ' --- ' + self.url

    # Used for displaying values in admin view
    def get_languages(self):
        return ", ".join(l.name for l in self.language.all())
    get_languages.short_description = "Languages"

    # Used for displaying values in admin view
    def get_geographies(self):
        return ", ".join(g.name for g in self.geography.all())
    get_geographies.short_description = "Geographies"

    class Meta:
        unique_together = ("url", "active_start_date")


class SiteGeoZone(models.Model):
    """
    Junction table for a site and GeoZones.
    """
    site = models.ForeignKey('Site', on_delete=models.CASCADE)
    geo_zone = models.ForeignKey('GeoZone', on_delete=models.CASCADE)

    def __str__(self):
        return self.site.url + '---' + self.geo_zone.name


class SiteLanguage(models.Model):
    """
    Junction table for a site and Languages.
    """
    site = models.ForeignKey('Site', on_delete=models.CASCADE)
    language = models.ForeignKey('Language', on_delete=models.CASCADE)

    def __str__(self):
        return self.site.url + '---' + self.language.name


class SiteSummarySnapshot(models.Model):
    """
    Object representing a snapshot of the aggregate statistics of all sites known at the time.
    """
    timestamp = models.DateTimeField(default=datetime.now)
    num_sites = models.IntegerField()
    num_courses = models.IntegerField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return str(self.timestamp) + '---' + str(self.num_sites) + '---' + str(self.num_courses)


# Models for referrer logs

class AccessLogAggregate(models.Model):
    """
    A model representing an aggregate access log entry of S3 Open edX logo referrals.
    """
    domain = models.CharField(max_length=255, null=True, blank=True, default=None)
    access_date = models.DateField(null=True, blank=True, default=None)
    filename = models.CharField(max_length=255, null=True, blank=True, default=None)
    access_count = models.IntegerField(null=True, blank=True, default=None)
    create_dt = models.DateTimeField(default=datetime.now)

    class Meta:
        unique_together = ("domain", "access_date", "filename")


class FilenameLog(models.Model):
    """
    A model representing a file name.
    """
    filename = models.CharField(max_length=255, unique=True)
