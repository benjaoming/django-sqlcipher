from django.core.management.commands.runserver import Command as RunserverCommand

from ._mixins import PromptForPragmaKeyMixin

class Command(PromptForPragmaKeyMixin, RunserverCommand):
    pass
