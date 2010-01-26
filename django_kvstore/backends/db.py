"""
Database key-value store backend.

Example configuration for Django settings:

    KEY_VALUE_STORE_BACKEND = 'db://table_name'

You will need to create a database table for storing the key-value pairs
when using this backend. The table should have two columns, 'kee' - capable of
storing up to 255 characters, and 'value', which should be a text type
(character blob). You can declare a regular Django model for this table, if
you want Django's ``syncdb`` command to create it for you. Just make sure the
table name Django uses is the same table name provided in the
``KEY_VALUE_STORE_BACKEND`` setting.
"""

import base64
from django_kvstore.backends.base import BaseStorage
from django.db import connection, transaction, DatabaseError
try:
    import cPickle as pickle
except ImportError:
    import pickle

class StorageClass(BaseStorage):
    def __init__(self, table, params):
        BaseStorage.__init__(self, params)
        self._table = table

    def get(self, key):
        cursor = connection.cursor()
        cursor.execute("SELECT kee, value FROM %s WHERE kee = %%s" % self._table, [key])
        row = cursor.fetchone()
        if row is None:
            return None
        return pickle.loads(base64.decodestring(row[1]))

    def set(self, key, value):
        encoded = base64.encodestring(pickle.dumps(value, 2)).strip()
        cursor = connection.cursor()
        cursor.execute("SELECT kee FROM %s WHERE kee = %%s" % self._table, [key])
        try:
            if cursor.fetchone():
                cursor.execute("UPDATE %s SET value = %%s WHERE kee = %%s" % self._table, [encoded, key])
            else:
                cursor.execute("INSERT INTO %s (kee, value) VALUES (%%s, %%s)" % self._table, [key, encoded])
        except DatabaseError, e:
            # To be threadsafe, updates/inserts are allowed to fail silently
            return False
        else:
            transaction.commit_unless_managed()
            return True

    def delete(self, key):
        cursor = connection.cursor()
        cursor.execute("DELETE FROM %s WHERE kee = %%s" % self._table, [key])
        transaction.commit_unless_managed()

    def has_key(self, key):
        cursor = connection.cursor()
        cursor.execute("SELECT kee FROM %s WHERE kee = %%s" % self._table, [key])
        return cursor.fetchone() is not None
