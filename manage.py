#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bubbles.settings")
    os.environ.setdefault('DJANGO_CONFIGURATION', 'Dev')
    #from django.core.management import execute_from_command_line
    from configurations.management import execute_from_command_line

    execute_from_command_line(sys.argv)
