# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function


from sqlcipher.utils import ensure_pragma_key


class PromptForPragmaKeyMixin(object):
    """""
    This is a universal command that you can have other management commands
    inherit from in case they need database access.
    """

    def handle(self, *args, **options):
        ensure_pragma_key()
        super(PromptForPragmaKeyMixin, self).handle(*args, **options)
