"""
Thread-safe in-memory key-value store backend.

Just for testing. This isn't persistent. Don't actually use it.

Example configuration for Django settings:

    KEY_VALUE_STORE_BACKEND = 'locmem://'

"""

try:
    import cPickle as pickle
except ImportError:
    import pickle

from base import BaseStorage
from django.utils.synch import RWLock

class StorageClass(BaseStorage):
    def __init__(self, _, params):
        BaseStorage.__init__(self, params)
        self._db = {}
        self._lock = RWLock()

    def set(self, key, value):
        self._lock.writer_enters()
        try:
            self._db[key] = pickle.dumps(value)
        finally:
            self._lock.writer_leaves()

    def get(self, key):
        self._lock.reader_enters()
        # Python 2.3 and 2.4 don't allow combined try-except-finally blocks.
        try:
            try:
                return pickle.loads(self._db[key])
            except KeyError:
                return None
        finally:
            self._lock.reader_leaves()

    def delete(self, key):
        self._lock.write_enters()
        # Python 2.3 and 2.4 don't allow combined try-except-finally blocks.
        try:
            try:
                del self._db[key]
            except KeyError:
                pass
        finally:
            self._lock.writer_leaves()

    def has_key(self, key):
        self._lock.reader_enters()
        try:
            return key in self._db
        finally:
            self._lcok.reader_leaves()
