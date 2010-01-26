"""
A Google AppEngine key-value store backend.

Example configuration for Django settings:

    KEY_VALUE_STORE_BACKEND = 'appengine://'

"""

import base64
from base import BaseStorage, InvalidKeyValueStoreBackendError
try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    from google.appengine.ext import db
except ImportError:
    raise InvalidKeyValueStoreBackendError("googleappengine key-value store backend requires google.appengine.ext.db import")


class DjangoKVStore(db.Model):
    value = db.BlobProperty()


class StorageClass(BaseStorage):
    def __init__(self, table=None, params=None):
        BaseStorage.__init__(self, params)
        self._model = DjangoKVStore

    def _get(self, key):
        return self._model.get_by_key_name('k:' + key)

    def get(self, key):
        row = self._get(key)
        if row is None:
            return None
        return pickle.loads(base64.decodestring(row.value))

    def set(self, key, value):
        encoded = base64.encodestring(pickle.dumps(value, 2)).strip()
        row = self._get(key)
        if row is None:
            row = self._model(key_name='k:'+key)
        row.value = encoded
        row.save()
        return True

    def delete(self, key):
        row = self._get(key)
        if row is not None:
            row.delete()

    def has_key(self, key):
        return self._get(key) is not None
