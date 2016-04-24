# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from django.conf import settings
from getpass import getpass


class PromptForPragmaKeyMixin(object):
    """""
    This is a universal command that you can have other management commands
    inherit from in case they need database access.
    """

    def handle(self, *args, **options):
        if not hasattr(settings, 'PRAGMA_KEY') or not settings.PRAGMA_KEY:
            print("There is no SQL Cipher key defined, it's unsafe to store in your settings. Please input your key")
            key = getpass("Key: ")
            settings.PRAGMA_KEY = key
        super(PromptForPragmaKeyMixin, self).handle(*args, **options)
