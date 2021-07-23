import django
from django.apps import AppConfig


class SlackdataConfig(AppConfig):
    name = 'slackdata'
    if django.VERSION >= (3, 2):
        default = False
