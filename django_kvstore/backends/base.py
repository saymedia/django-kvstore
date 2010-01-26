"Base key-value store abstract class."

from django.core.exceptions import ImproperlyConfigured

class InvalidKeyValueStoreBackendError(ImproperlyConfigured):
    pass

class BaseStorage(object):
    def __init__(self, *args, **kwargs):
        pass

    def set(self, key, value):
        """Set a value in the key-value store."""
        raise NotImplementedError

    def delete(self, key):
        """Delete a key from the key-value store. Fail silently."""
        raise NotImplementedError

    def has_key(self, key):
        """Returns True if the key is in the store."""
        return self.get(key) is not None

    def __contains__(self, key):
        """Returns true if the key is in the store."""
        return self.has_key(key)
