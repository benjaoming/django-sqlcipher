
from django.core.management.commands.migrate import Command as BaseCommand

from ._mixins import PromptForPragmaKeyMixin


class Command(PromptForPragmaKeyMixin, BaseCommand):
    """
    Before migrating, we need to know the pragma key to access the database. If
    it does not exist, retrieve it from command line input.
    """
    pass
