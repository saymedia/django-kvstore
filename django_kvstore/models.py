from django_kvstore import kvstore


class FieldError(Exception): pass

KV_PREFIX = '__KV_STORE_::'

def generate_key(cls, pk):
    return str('%s%s.%s:%s' % (KV_PREFIX, cls.__module__, cls.__name__, pk))


class Field(object):
    def __init__(self, default=None, pk=False):
        self.default = default
        self.pk = pk

    def install(self, name, cls):
        setattr(cls, name, self.default)

    def decode(self, value):
        """Decodes an object from the datastore into a python object."""
        return value
    
    def encode(self, value):
        """Encodes an object into a value suitable for the backend datastore."""
        return value


class ModelMetaclass(type):
    """
    Metaclass for `kvstore.models.Model` instances. Installs 
    `kvstore.models.Field` and `kvstore.models.Key` instances
    declared as attributes of the new class.

    """

    def __new__(cls, name, bases, attrs):
        fields = {}

        for base in bases:
            if isinstance(base, ModelMetaclass):
                fields.update(base.fields)

        new_fields = {}
        # Move all the class's attributes that are Fields to the fields set.
        for attrname, field in attrs.items():
            if isinstance(field, Field):
                new_fields[attrname] = field
                if field.pk:
                    # Add key_field attr so we know what the key is
                    if 'key_field' in attrs:
                        raise FieldError("Multiple key fields defined for model '%s'" % name)
                    attrs['key_field'] = attrname
            elif attrname in fields:
                # Throw out any parent fields that the subclass defined as
                # something other than a field
                del fields[attrname]

        fields.update(new_fields)
        attrs['fields'] = fields
        new_cls = super(ModelMetaclass, cls).__new__(cls, name, bases, attrs)

        for field, value in new_fields.items():
            new_cls.add_to_class(field, value)

        return new_cls

    def add_to_class(cls, name, value):
        if hasattr(value, 'install'):
            value.install(name, cls)
        else:
            setattr(cls, name, value)


class Model(object):

    __metaclass__ = ModelMetaclass

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)

    def to_dict(self):
        d = {}
        for name, field in self.fields.items():
            d[name] = field.encode(getattr(self, name))
        return d

    def save(self):
        d = self.to_dict()
        kvstore.set(generate_key(self.__class__, self._get_pk_value()), d)

    def _get_pk_value(self):
        return getattr(self, self.key_field)

    @classmethod
    def from_dict(cls, fields):
        for name, value in fields.items():
            # Keys can't be unicode to work as **kwargs. Must delete and re-add
            # otherwise the dict won't change the type of the key.
            if name in cls.fields:
                if isinstance(name, unicode):
                    del fields[name]
                    name = name.encode('utf-8')
                fields[name] = cls.fields[name].decode(value)
            else:
                del fields[name]
        return cls(**fields)

    @classmethod
    def get(cls, id):
        fields = kvstore.get(generate_key(cls, id))
        if fields is None:
            return None
        return cls.from_dict(fields)
