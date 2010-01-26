"""
Memcache key-value store backend

Just for testing. This isn't persistent. Don't actually use it.

Example configuration for Django settings:

    KEY_VALUE_STORE_BACKEND = 'tokyotyrant://hostname:port

"""

from base import BaseStorage, InvalidKeyValueStoreBackendError
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import smart_unicode, smart_str
from django.utils import simplejson

try:
    import pytyrant
except ImportError:
    raise InvalidKeyValueStoreBackendError("Tokyotyrant key-value store backend requires the 'pytyrant' library")

class StorageClass(BaseStorage):
    def __init__(self, server, params):
        BaseStorage.__init__(self, params)
        host, port = server.split(':')
        try:
            port = int(port)
        except ValueError:
            raise ImproperlyConfigured("Invalid port provided for tokyo-tyrant key-value store backend")
        self._db = pytyrant.PyTyrant.open(host, port)

    def set(self, key, value):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        self._db[smart_str(key)] = simplejson.dumps(value)

    def get(self, key):
        val = self._db.get(smart_str(key))
        if isinstance(val, basestring):
            return simplejson.loads(val)
        else:
            return val

    def delete(self, key):
        del self._db[smart_str(key)]

    def close(self, **kwargs):
        pass
        # Er, should be closing after each request..? But throws
        # a 'Bad File Descriptor' exception if we do (presumably because
        # something's trying to use a connection that's already been
        # closed...
        #self._db.close()
