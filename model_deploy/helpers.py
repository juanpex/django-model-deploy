# -*- coding: utf-8 -*-
from django.db.models import AutoField
from django.db.models.fields.files import FieldFile


class Missing:
    pass


def copy_model_instance(obj):
    initial = dict([(f.name, getattr(obj, f.name))
                    for f in obj._meta.fields
                    if not isinstance(f, AutoField) and
                    not f in obj._meta.parents.values()])
    return obj.__class__(**initial)


def diff(instance1, instance2=None, missing_field=None):
    '''
    Compares two instances and returns a dictionary of
    the different fields and a tuple of the corrisponding values.

    If a instance2 is not provided, the first instance is compared
    against the current values in the database.

    Set "missing_field" to differentiate between a field that doesn't
    exist and a field that contains a None.
    '''
    if not instance2:
        if not instance1.pk:
            return {}  # nothing to compare, dur.
        instance2 = instance1.__class__._default_manager.filter(pk=instance1.pk).get()
    d = {}
    for name, field in set(instance1._meta._name_map.items() + instance2._meta._name_map.items()):
        value1 = missing_field
        value2 = missing_field
        if field[0].__class__.__name__ == 'ManyToManyField':
            try:
                objects = getattr(instance1, name, missing_field)
                if objects != missing_field:
                    value1 = list(objects.values())
            except Exception as e:
                value1 = e
            try:
                objects = getattr(instance2, name, missing_field)
                if objects != missing_field:
                    value2 = list(objects.values())
            except Exception as e:
                value2 = e
        elif  field[0].__class__.__name__ not in ['OneToOneField', 'AutoField', 'RelatedField']:
            try:
                value1 = getattr(instance1, name, missing_field)
            except Exception as e:
                value1 = e
            try:
                value2 = getattr(instance2, name, missing_field)
            except Exception as e:
                value2 = e

        if value1 != value2:
            # do they break in the same way?
            if isinstance(value1, Exception) and isinstance(value2, Exception):
                if type(value1) != type(value2):
                    # different type of exceptions
                    d[name] = (value1, value2)
            else:
                if isinstance(getattr(instance1, name), FieldFile):
                    value1 = value1.name
                    value2 = value2.name
                # actually different values
                d[name] = (value1, value2)

    return d
