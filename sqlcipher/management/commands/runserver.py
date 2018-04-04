from django.core.management.commands.runserver import Command as RunserverCommand

from ._mixins import ensure_pragma_key


class Command(RunserverCommand):

    def inner_run(self, *args, **options):
        ensure_pragma_key()
        RunserverCommand.inner_run(self, *args, **options)
