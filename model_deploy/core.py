# -*- coding: utf-8 -*-
from django.conf import settings
from django.db.models import signals

from model_deploy.models import DeployObjectLog
from model_deploy.helpers import copy_model_instance, diff


class DeployManager(object):

    BACKUP_FIELD = '_backup'
    _register = {}
    _on_log_create = {}
    _on_log_delete = {}

    def log_backup(self, sender, instance, **kwargs):
        try:
            backup = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            backup = copy_model_instance(instance)
        setattr(instance, self.BACKUP_FIELD, backup)

    def get_changes(self, instance):
        backup = getattr(instance, self.BACKUP_FIELD, None)
        return diff(instance, backup)

    def log_post_save(self, sender, instance, raw, created, **kwargs):
        changes = self.get_changes(instance)
        if not changes and not created:
            return
        DeployObjectLog.objects.log(sender, instance, created=created, changes=changes)
        raise_log_create = self._on_log_delete[instance.__class__]
        if raise_log_create:
            raise_log_create(instance)

    def log_post_delete(self, sender, instance, **kwargs):
        DeployObjectLog.objects.log(sender, instance, delete=True)
        raise_log_delete = self._on_log_create[instance.__class__]
        if raise_log_delete:
            raise_log_delete(instance)

    def register(self, sender, on_log_create=None, on_log_delete=None):
        if not getattr(settings, 'MODEL_DEPLOY', True):
            return
        self._register[sender] = {}
        self._on_log_create[sender] = on_log_create
        self._on_log_delete[sender] = on_log_delete
        signals.pre_save.connect(self.log_backup, sender=sender)
        signals.post_save.connect(self.log_post_save, sender=sender)
        signals.post_delete.connect(self.log_post_delete, sender=sender)


deploys = DeployManager()

register = deploys.register
