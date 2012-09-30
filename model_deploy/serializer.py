# -*- coding: utf-8 -*-
import os
import base64
from StringIO import StringIO

from django.conf import settings
from django.utils import simplejson
from django.core.files.base import ContentFile
from django.db import models, DEFAULT_DB_ALIAS
from django.utils.encoding import smart_unicode
from django.db.models.fields.files import FileField
from django.core.serializers.python import _get_model
from django.core.serializers.base import DeserializedObject
from django.core.serializers.json import Serializer as DJSerializer, DeserializationError


class Serializer(DJSerializer):

    def serialize(self, queryset, **options):
        """
        Serialize a queryset.
        """
        self.options = options

        self.stream = options.pop("stream", StringIO())
        self.selected_fields = options.pop("fields", None)
        self.use_natural_keys = options.pop("use_natural_keys", False)

        self.start_serialization()
        for obj, changes, action in queryset:
            if action == 0:
                changes = []
            else:
                changes = eval(changes).keys()
            self.start_object(obj)
            # Use the concrete parent class' _meta instead of the object's _meta
            # This is to avoid local_fields problems for proxy models. Refs #17717.
            concrete_model = obj._meta.concrete_model
            for field in concrete_model._meta.local_fields:
                if field.serialize:
                    if field.rel is None:
                        if self.selected_fields is None or field.attname in self.selected_fields:
                            self.handle_field(obj, field, changes, action)
                    else:
                        if self.selected_fields is None or field.attname[:-3] in self.selected_fields:
                            self.handle_fk_field(obj, field)
            for field in concrete_model._meta.many_to_many:
                if field.serialize:
                    if self.selected_fields is None or field.attname in self.selected_fields:
                        self.handle_m2m_field(obj, field)
            self.end_object(obj, changes, action)
        self.end_serialization()
        return self.getvalue()

    def handle_field(self, obj, field, changes, action):
        super(Serializer, self).handle_field(obj, field)
        if isinstance(field, FileField):
            fileobj = getattr(obj, field.name)
            if fileobj:
                imagedata = ""
                if field.name in changes or action == 1:
                    imagedata = open(fileobj.path, "rb").read().encode("base64")
                self._current[field.name] = {
                    'data': imagedata,
                    'name': os.path.basename(fileobj.name)
                }

    def end_object(self, obj, changes=None, action=None):
        self.objects.append({
            'model': smart_unicode(obj._meta),
            'pk': smart_unicode(obj._get_pk_val(), strings_only=True),
            'fields': self._current,
            'changes': changes,
            'action': action
        })
        self._current = None


def Deserializer(stream_or_string, **options):
    """
    Deserialize a stream or string of JSON data.
    """
    if isinstance(stream_or_string, basestring):
        stream = StringIO(stream_or_string)
    else:
        stream = stream_or_string
    try:
        for obj in CustomDeserializer(simplejson.load(stream), **options):
            yield obj
    except GeneratorExit:
        raise
    except Exception, e:
        # Map to deserializer error
        raise DeserializationError(e)


def CustomDeserializer(object_list, **options):
    """
    Deserialize simple Python objects back into Django ORM instances.

    It's expected that you pass the Python objects themselves (instead of a
    stream or a string) to the constructor
    """
    db = options.pop('using', DEFAULT_DB_ALIAS)
    models.get_apps()
    for d in object_list:
        # Look up the model and starting build a dict of data for it.
        Model = _get_model(d["model"])
        data = {Model._meta.pk.attname: Model._meta.pk.to_python(d["pk"])}
        m2m_data = {}
        filefields = []

        # Handle each field
        for (field_name, field_value) in d["fields"].iteritems():
            if isinstance(field_value, str):
                field_value = smart_unicode(field_value, options.get("encoding", settings.DEFAULT_CHARSET), strings_only=True)

            field = Model._meta.get_field(field_name)

            # Handle M2M relations
            if field.rel and isinstance(field.rel, models.ManyToManyRel):
                if hasattr(field.rel.to._default_manager, 'get_by_natural_key'):
                    def m2m_convert(value):
                        if hasattr(value, '__iter__'):
                            return field.rel.to._default_manager.db_manager(db).get_by_natural_key(*value).pk
                        else:
                            return smart_unicode(field.rel.to._meta.pk.to_python(value))
                else:
                    m2m_convert = lambda v: smart_unicode(field.rel.to._meta.pk.to_python(v))
                m2m_data[field.name] = [m2m_convert(pk) for pk in field_value]

            # Handle FK fields
            elif field.rel and isinstance(field.rel, models.ManyToOneRel):
                if field_value is not None:
                    if hasattr(field.rel.to._default_manager, 'get_by_natural_key'):
                        if hasattr(field_value, '__iter__'):
                            obj = field.rel.to._default_manager.db_manager(db).get_by_natural_key(*field_value)
                            value = getattr(obj, field.rel.field_name)
                            # If this is a natural foreign key to an object that
                            # has a FK/O2O as the foreign key, use the FK value
                            if field.rel.to._meta.pk.rel:
                                value = value.pk
                        else:
                            value = field.rel.to._meta.get_field(field.rel.field_name).to_python(field_value)
                        data[field.attname] = value
                    else:
                        data[field.attname] = field.rel.to._meta.get_field(field.rel.field_name).to_python(field_value)
                else:
                    data[field.attname] = None

            elif isinstance(field, FileField):
                if field_value:
                    if field.name in d["changes"] or d["action"] == 1:
                        filefields.append([field, field_value['name'], ContentFile(base64.decodestring(field_value['data']))])
                    else:
                        filefields.append([field, field_value['name'], None])
                else:
                    filefields.append([field, None, None])
            else:
                data[field.name] = field.to_python(field_value)

        yield CustomDeserializedObject(Model(**data), m2m_data, filefields)


class CustomDeserializedObject(DeserializedObject):

    def __init__(self, obj, m2m_data=None, file_data=[]):
        self.object = obj
        self.m2m_data = m2m_data
        self.file_data = file_data

    def save(self, save_m2m=True, using=None):
        for field, filename, djangofile in self.file_data:
            filefield = getattr(self.object, field.name)
            if filename and not djangofile:
                current_file = getattr(self.object.__class__.objects.get(pk=self.object.pk), field.name)
                setattr(self.object, field.name, current_file)
                filefield = getattr(self.object, field.name)
            elif filename and djangofile:
                filefield.save(filename, djangofile, save=False)

        models.Model.save_base(self.object, using=using, raw=True)
        if self.m2m_data and save_m2m:
            for accessor_name, object_list in self.m2m_data.items():
                setattr(self.object, accessor_name, object_list)

        # prevent a second (possibly accidental) call to save() from saving
        # the m2m data twice.
        self.m2m_data = None
        self.file_data = None
