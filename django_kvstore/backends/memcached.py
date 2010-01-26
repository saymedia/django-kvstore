"""
Memcache key-value store backend

Just for testing. This isn't persistent. Don't actually use it.

Example configuration for Django settings:

    KEY_VALUE_STORE_BACKEND = 'memcached://hostname:port'

"""

from base import BaseStorage, InvalidKeyValueStoreBackendError
from django.utils.encoding import smart_unicode, smart_str

try:
    import cmemcache as memcache
except ImportError:
    try:
        import memcache
    except:
        raise InvalidKeyValueStoreBackendError("Memcached key-value store backend requires either the 'memcache' or 'cmemcache' library")

class StorageClass(BaseStorage):
    def __init__(self, server, params):
        BaseStorage.__init__(self, params)
        self._db = memcache.Client(server.split(';'))

    def set(self, key, value):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        self._db.set(smart_str(key), value, 0)

    def get(self, key):
        val = self._db.get(smart_str(key))
        if isinstance(val, basestring):
            return smart_unicode(val)
        else:
            return val

    def delete(self, key):
        self._db.delete(smart_str(key))

    def close(self, **kwargs):
        self._db.disconnect_all()
