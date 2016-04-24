from django.core.management.commands.loaddata import Command as LoaddataCommand

from ._mixins import PromptForPragmaKeyMixin

class Command(PromptForPragmaKeyMixin, LoaddataCommand):
    pass
