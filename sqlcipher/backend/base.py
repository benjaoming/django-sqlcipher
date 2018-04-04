from __future__ import unicode_literals

from django.db.backends.sqlite3.base import DatabaseWrapper as BaseDatabaseWrapper, \
    _sqlite_date_extract, _sqlite_date_trunc, _sqlite_datetime_cast_date, \
    _sqlite_datetime_extract, _sqlite_datetime_trunc, _sqlite_time_extract, \
    _sqlite_regexp, _sqlite_format_dtdelta, _sqlite_power, FORMAT_QMARK_REGEX


from pysqlcipher import dbapi2 as Database


import datetime
import decimal
import warnings

from django.conf import settings
from django.db.backends import utils as backend_utils
from django.utils import six, timezone
from django.utils.dateparse import (
    parse_date, parse_datetime, parse_time,
)
from django.utils.deprecation import RemovedInDjango20Warning
from django.utils.safestring import SafeBytes

try:
    import pytz
except ImportError:
    pytz = None

DatabaseError = Database.DatabaseError
IntegrityError = Database.IntegrityError


def adapt_datetime_warn_on_aware_datetime(value):
    # Remove this function and rely on the default adapter in Django 2.0.
    if settings.USE_TZ and timezone.is_aware(value):
        warnings.warn(
            "The SQLite database adapter received an aware datetime (%s), "
            "probably from cursor.execute(). Update your code to pass a "
            "naive datetime in the database connection's time zone (UTC by "
            "default).", RemovedInDjango20Warning)
        # This doesn't account for the database connection's timezone,
        # which isn't known. (That's why this adapter is deprecated.)
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
    return value.isoformat(str(" "))


def decoder(conv_func):
    """ The Python sqlite3 interface returns always byte strings.
        This function converts the received value to a regular string before
        passing it to the receiver function.
    """
    return lambda s: conv_func(s.decode('utf-8'))


Database.register_converter(str("bool"), decoder(lambda s: s == '1'))
Database.register_converter(str("time"), decoder(parse_time))
Database.register_converter(str("date"), decoder(parse_date))
Database.register_converter(str("datetime"), decoder(parse_datetime))
Database.register_converter(str("timestamp"), decoder(parse_datetime))
Database.register_converter(str("TIMESTAMP"), decoder(parse_datetime))
Database.register_converter(str("decimal"), decoder(backend_utils.typecast_decimal))

Database.register_adapter(datetime.datetime, adapt_datetime_warn_on_aware_datetime)
Database.register_adapter(decimal.Decimal, backend_utils.rev_typecast_decimal)
if six.PY2:
    Database.register_adapter(str, lambda s: s.decode('utf-8'))
    Database.register_adapter(SafeBytes, lambda s: s.decode('utf-8'))


class DatabaseWrapper(BaseDatabaseWrapper):
    Database = Database

    def create_cursor(self, name=None):
        pragma_sql = "PRAGMA key='%s';" % (settings.PRAGMA_KEY,)
        cursor = self.connection.cursor(factory=SQLiteCursorWrapper)
        cursor.execute(pragma_sql)
        cursor.close()
        cursor = self.connection.cursor(factory=SQLiteCursorWrapper)
        return cursor

    def get_new_connection(self, conn_params):
        conn = Database.connect(**conn_params)
        conn.create_function("django_date_extract", 2, _sqlite_date_extract)
        conn.create_function("django_date_trunc", 2, _sqlite_date_trunc)
        conn.create_function("django_datetime_cast_date", 2, _sqlite_datetime_cast_date)
        conn.create_function("django_datetime_extract", 3, _sqlite_datetime_extract)
        conn.create_function("django_datetime_trunc", 3, _sqlite_datetime_trunc)
        conn.create_function("django_time_extract", 2, _sqlite_time_extract)
        conn.create_function("regexp", 2, _sqlite_regexp)
        conn.create_function("django_format_dtdelta", 3, _sqlite_format_dtdelta)
        conn.create_function("django_power", 2, _sqlite_power)
        return conn


class SQLiteCursorWrapper(Database.Cursor):
    """
    Django uses "format" style placeholders, but pysqlite2 uses "qmark" style.
    This fixes it -- but note that if you want to use a literal "%s" in a query,
    you'll need to use "%%s".
    """
    def execute(self, query, params=None):
        if params is None:
            return Database.Cursor.execute(self, query)
        query = self.convert_query(query)
        return Database.Cursor.execute(self, query, params)

    def executemany(self, query, param_list):
        query = self.convert_query(query)
        return Database.Cursor.executemany(self, query, param_list)

    def convert_query(self, query):
        return FORMAT_QMARK_REGEX.sub('?', query).replace('%%', '%')
