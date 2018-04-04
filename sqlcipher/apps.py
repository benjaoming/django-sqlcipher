from __future__ import unicode_literals

from django.apps import AppConfig
from django.conf import settings
from django.db.backends.signals import connection_created


class SQLCipherConfig(AppConfig):

    name = 'sqlcipher'

    def ready(self):
        """
        Sets up PRAGMAs.
        """
        connection_created.connect(self.activate_pragmas_per_connection)

    @staticmethod
    def activate_pragmas_per_connection(sender, connection, **kwargs):

        if connection.vendor == "sqlite":
            pragma_sql = "PRAGMA key='%s';" % (settings.PRAGMA_KEY,)
            cursor = connection.cursor()
            cursor.execute(pragma_sql)
            cursor.close()
