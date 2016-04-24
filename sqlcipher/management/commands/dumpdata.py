from django.core.management.commands.dumpdata import Command as DumpdataCommand

from ._mixins import PromptForPragmaKeyMixin

class Command(PromptForPragmaKeyMixin, DumpdataCommand):
    pass
