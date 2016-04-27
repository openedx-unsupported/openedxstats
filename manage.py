#!/usr/bin/env python
import os
import sys

from dotenv import load_dotenv

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "slack-stats.settings")

    dotenv_path = os.path.join(os.path.dirname(__file__), 'slack-stats/.env')
    load_dotenv(dotenv_path)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
