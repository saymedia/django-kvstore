"""
Amazon SimpleDB key-value store backend

Example configuration for Django settings:

    KEY_VALUE_STORE_BACKEND = 'sdb://<simpledb_domain>?aws_access_key=<access_key>&aws_secret_access_key=<secret_key>'

"""


from base import BaseStorage, InvalidKeyValueStoreBackendError
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import smart_unicode, smart_str
from django.utils import simplejson

try:
    import simpledb
except ImportError:
    raise InvalidKeyValueStoreBackendError("SipmleDB key-value store backend requires the 'python-simpledb' library")

class StorageClass(BaseStorage):
    def __init__(self, domain, params):
        BaseStorage.__init__(self, params)
        params = dict(params)
        try:
            aws_access_key = params['aws_access_key']
            aws_secret_access_key = params['aws_secret_access_key']
        except KeyError:
            raise ImproperlyConfigured("Incomplete configuration of SimpleDB key-value store. Required parameters: 'aws_access_key', and 'aws_secret_access_key'.")
        self._db = simpledb.SimpleDB(aws_access_key, aws_secret_access_key)
        self._domain = self._db[domain]

    def set(self, key, value):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        self._domain[smart_str(key)] = {'value': simplejson.dumps(value)}

    def get(self, key):
        val = self._domain[smart_str(key)].get('value', None)
        if isinstance(val, basestring):
            return simplejson.loads(val)
        else:
            return val

    def delete(self, key):
        del self._domain[smart_str(key)]

    def close(self, **kwargs):
        pass
