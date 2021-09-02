"""
WSGI config for openedxstats project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""
import os

from os.path import abspath, dirname, join
from sys import path

import environ

SITE_ROOT = dirname(dirname(abspath(__file__)))
path.append(SITE_ROOT)

env_file_path = join(dirname(__file__), '.env')
environ.Env.read_env(env_file_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openedxstats.settings")


from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
