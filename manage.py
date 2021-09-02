#!/usr/bin/env python
import os
import sys

import environ

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openedxstats.settings")

    env_file_path = os.path.join(os.path.dirname(__file__), 'openedxstats/.env')
    environ.Env.read_env(env_file_path)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
