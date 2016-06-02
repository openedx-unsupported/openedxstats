from __future__ import unicode_literals

from django.db import models
import datetime


# Create your models here.


class Site(models.Model):
    """
    A model describing an open edX website.
    """
    COURSE_TYPE_CHOICES = (
        ('MOOC', 'MOOC'),
        ('SPOC', 'SPOC'),
        ('Both', 'Both'),
        ('Unknown', 'Unknown'),
    )

    #id = models.IntegerField()    <--- Django automatically creates a serial id in postgres? Not known
    site_type = models.CharField(max_length=255)



    """

CREATE TYPE course_type_enum AS ENUM ('MOOC', 'SPOC', 'both', 'unknown');

CREATE TABLE IF NOT EXISTS sites(
    id SERIAL PRIMARY KEY NOT NULL,
    site_type Varchar(255) NOT NULL DEFAULT 'General',
    name Varchar(255) UNIQUE NOT NULL,
    url Varchar(255) UNIQUE NOT NULL,
    course_count Integer,
    last_checked timestamp NOT NULL,
    org_type Varchar(255),
    github_fork Varchar(255),
    notes text,
    course_type course_type_enum,
    registered_user_count Integer,
    active_learner_count Integer
);

CREATE TABLE IF NOT EXISTS geo_zones(
    name Varchar(255) PRIMARY KEY NOT NULL
);

CREATE TABLE IF NOT EXISTS languages(
    name Varchar(255) PRIMARY KEY NOT NULL
);

CREATE TABLE IF NOT EXISTS site_geo_zone(
    site_id Integer REFERENCES sites(id),
    geo_zone_name Varchar(255) REFERENCES geo_zones(name)
);

CREATE TABLE IF NOT EXISTS language_name(
    site_id Integer REFERENCES sites(id),
    language_name Varchar(255) REFERENCES languages(name)
);
    """