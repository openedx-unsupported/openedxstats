"""
WSGI config for openedxstats project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""
import os

from os.path import abspath, dirname, join
from sys import path

import dotenv

SITE_ROOT = dirname(dirname(abspath(__file__)))
path.append(SITE_ROOT)

dotenv_path = join(dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openedxstats.settings")


from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
