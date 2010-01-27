"""
Redis key-value store backend.

Example configuration for Django settings:

    KEY_VALUE_STORE_BACKEND = 'redis://hostname:port'

"""
import base64
from base import BaseStorage, InvalidKeyValueStoreBackendError
from django.utils.encoding import smart_unicode, smart_str

try:
    import redis
except ImportError:
    raise InvalidKeyValueStoreBackendError("The Redis key-value store backend requires the Redis python client.")

try:
    import cPickle as pickle
except ImportError:
    import pickle

class StorageClass(BaseStorage):

    def __init__(self, server, params):
        BaseStorage.__init__(self, params)
        self._db = redis.Redis(host=server, **params)

    def set(self, key, value):
        encoded = base64.encodestring(pickle.dumps(value, 2)).strip()
        self._db.set(smart_str(key), encoded)

    def get(self, key):
        val = self._db.get(smart_str(key))
        if val is None:
            return None
        return pickle.loads(base64.decodestring(val))

    def delete(self, key):
        self._db.delete(smart_str(key))

    def close(self, **kwargs):
        pass
