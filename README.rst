An extensible key-value store backend for Django applications.

This module provides an abstraction layer for accessing a key-value storage.

Configuring your key-value store is a matter of adding a statement in this
form to your Django settings module::

    KEY_VALUE_STORE_BACKEND = 'scheme://store?parameters'

Where ``scheme`` is one of the following, persistent stores:

* db (local table accessed through Django's database connection)
* googleappengine (Google AppEngine data store)
* sdb (Amazon SimpleDB)
* tokyotyrant (Tokyo Tyrant)
* redis (Redis)

And some non-persistent stores, provided mainly for testing purposes:

* locmem
* memcached

``store`` and ``parameters`` varies from one backend to another. Refer
to the documentation included in each backend implementation for further
details.

You can define a django_kvstore-backed custom model, in a fashion similar
to Django models (although it does not support querying, except by primary
key lookup).

Here's an example of a custom model class using django_kvstore::

    from django_kvstore import models

    class MyData(models.Model):
        my_key = models.Field(pk=True)
        foo = models.Field()
        bar = models.Field()

Typical usage for such a model::

    key = "something_unique"
    data = MyData.get(key)
    if data is None:
        data = MyData(my_key=key)
        data.foo = "foo"
        data.bar = "bar"
        data.save()

and deletion::

    key = "something_unique"
    data = MyData.get(key)
    if data is not None:
        data.delete()
