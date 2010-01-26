"""
An extensible key-value store backend for Django applications.

This package defines a set of key-value store backends that all conform to a
simple API. A key-value store is a simple data storage backend that is similar
to a cache. Unlike a cache, items are persisted to disk, and are not lost when
the backend restarts."""

__version__ = '1.0'
__date__ = '26 December 2010'
__author__ = 'Six Apart Ltd.'
__credits__ = """Mike Malone
Brad Choate"""

from cgi import parse_qsl
from django.conf import settings
from django.core import signals

# Names for use in settings file --> name of module in "backends" directory.
# Any backend scheeme that is not in this dictionary is treated as a Python
# import path to a custom backend.
BACKENDS = {
    'memcached': 'memcached',
    'tokyotyrant': 'tokyotyrant',
    'locmem': 'locmem',
    'db': 'db',
    'simpledb': 'sdb',
    'googleappengine': 'googleappengine',
}

class InvalidKeyValueStoreBackend(Exception): pass

def get_kvstore(backend_uri):
    if backend_uri.find(':') == -1:
        raise InvalidKeyValueStoreBackend("Backend URI must start with scheme://")
    scheme, rest = backend_uri.split(':', 1)
    if not rest.startswith('//'):
        raise InvalidKeyValueStoreBackend("Backend URI must start with scheme://")

    host = rest[2:]
    qpos = rest.find('?')
    if qpos != -1:
        params = dict(parse_qsl(rest[qpos+1:]))
        host = rest[2:qpos]
    else:
        params = {}
    if host.endswith('/'):
        host = host[:-1]

    if scheme in BACKENDS:
        module = __import__('django_kvstore.backends.%s' % BACKENDS[scheme], {}, {}, [''])
    else:
        module = __import__(scheme, {}, {}, [''])
    return getattr(module, 'StorageClass')(host, params)

kvstore = get_kvstore(settings.KEY_VALUE_STORE_BACKEND)
"""A handle to the configured key-value store."""

# Some kv store backends need to do a cleanup at the end of
# a request cycle. If the cache provides a close() method, wire
# it up here.
if hasattr(kvstore, 'close'):
    signals.request_finished.connect(kvstore.close)
