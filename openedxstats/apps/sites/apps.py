import django
from django.apps import AppConfig


class SitesConfig(AppConfig):
    name = 'sites'
    if django.VERSION >= (3, 2):
        default = False
