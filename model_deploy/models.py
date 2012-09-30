# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey


SERVER_CHOICES = [(key, values['name']) for key, values in getattr(settings, 'SERVERS', {}).items() if key != 'current']

ACTION_CHIOCES = (
    (1, _('Add')),
    (2, _('Change')),
    (0, _('Delete')),
)


class DeployObjectLogManager(models.Manager):

    def log(self, model, instance, created=False, delete=False, changes=None):
        ct = ContentType.objects.get_for_model(model)
        action = 2  # Change
        if created:
            action = 1  # Add
        if delete:
            action = 0  # Delete
        kwargs = {
            'content_type': ct,
            'server': getattr(settings, 'DEFAULT_DEPLOY_SERVER', ''),
            'action': action,
            'object_id': instance.pk,
            'content_object': instance,
            'changes': changes,
        }

        return self.model.objects.create(**kwargs)


class DeployObjectLog(models.Model):
    server = models.CharField(_('Server'), choices=SERVER_CHOICES, max_length=15)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    content_object = GenericForeignKey()
    object_id = models.CharField(_('Object id'), max_length=200)
    action = models.IntegerField(_('Action'), choices=ACTION_CHIOCES)
    action_time = models.DateTimeField(_('Action time'), default=datetime.datetime.now)
    deployed = models.BooleanField(_('Deployed?'), default=False)
    user = models.ForeignKey(User, verbose_name=_('Deployed by'), blank=True, null=True, editable=False)
    changes = models.TextField(_('Change fileds'), blank=True, null=True)

    objects = DeployObjectLogManager()

    def __unicode__(self):
        return u'[pk=%s] %s.%s' % (self.pk, self.content_type, self.object_id)


class DeleteObject(models.Model):
    id = models.TextField(primary_key=True)
    delete = models.BooleanField(default=True)
    app_label = models.TextField()
    model = models.TextField()

    class Meta:
        managed = False

    def __unicode__(self):
        return u'%s.%s.%s' % (self.app_label, self.model, self.id)
