#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Future Imports
from __future__ import unicode_literals, absolute_import

# Standard Library Imports
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
