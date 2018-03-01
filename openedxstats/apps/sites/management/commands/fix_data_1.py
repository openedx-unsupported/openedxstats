"""
The automated scraper didn't properly keep the languages and geographies when
making new entries for sites.  This command finds the old entries, and fixes
up the latest entries so we don't lose the information.
"""

import itertools

from django.core.management.base import BaseCommand

from ...models import Site, SiteLanguage, SiteGeoZone

def by_url(s):
    return s.url

class Command(BaseCommand):
    def handle(self, *args, **options):
        sites = sorted(Site.objects.all(), key=by_url)

        for url, usites in itertools.groupby(sites, key=by_url):
            usites_iter = iter(sorted(usites, key=lambda s: s.active_start_date, reverse=True))
            if 0:
                for usite in usites_iter:
                    print(f"   {usite.active_start_date:15}: "
                          f"{len(list(usite.language.all())):3}"
                          f"{len(list(usite.geography.all())):3}"
                          )

            the_site = next(usites_iter)
            languages = list(the_site.language.all())
            geographies = list(the_site.geography.all())
            if languages or geographies:
                print(f'{url}: ok {len(languages)}/{len(geographies)}')
                continue
            for old_site in usites_iter:
                languages = list(old_site.language.all())
                geographies = list(old_site.geography.all())
                if not languages and not geographies:
                    continue
                print(f'{url}: fixing from {old_site.active_start_date}: {len(languages)}/{len(geographies)}')
                for lang in languages:
                    SiteLanguage.objects.create(language=lang, site=the_site).save()
                for geo in geographies:
                    SiteGeoZone.objects.create(geo_zone=geo, site=the_site).save()
                break
            else:
                print(f'{url}: no languages')
