from .base import *  # noqa


ADMINS = (
    ('Joel Barciauskas', 'joel@edx.org'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'openedxstats',
        'USER': 'joelbarciauskas',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}


# You might want to use sqlite3 for testing in local as it's much faster.
if IN_TESTING:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/openedxstats_test.db',
        }
    }

SLACK_API_TOKEN = os.environ.get("SLACK_API_TOKEN")
