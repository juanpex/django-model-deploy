# -*- coding: utf-8 -*-
import requests
from collections import OrderedDict

from django.conf import settings
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from model_deploy.serializer import Serializer
from model_deploy.models import DeleteObject


@transaction.commit_on_success
def deploytoserver(objects, server, user=None):
    count = 0
    response = None
    SERVERS = getattr(settings, 'SERVERS', {})

    if not SERVERS:
        raise ValueError(_('There are no SERVERS in your settings file'))

    if not server:
        raise ValueError(_('Provide a server key.'))

    if not server in SERVERS:
        raise ValueError(_('Server key "%s" does not exist in your settings.' % server))

    server_conf = SERVERS.get(server)

    objects = objects.filter(deployed=False)

    if objects.exists():

        def fill_obj(obj):
            if obj.action == 0:
                newobj = DeleteObject()
                newobj.id = obj.object_id
                newobj.delete = True
                newobj.app_label = obj.content_type.app_label
                newobj.model = obj.content_type.model
                return newobj
            return obj.content_object

        deploy_objects = OrderedDict()

        for obj in objects:
            instance = fill_obj(obj)
            deploy_objects[unicode(instance)] = (instance, obj.changes, obj.action)

        post_json = Serializer().serialize(deploy_objects.values())

        put_kwargs = {
            'url': server_conf['url'],
            'headers': {'Content-type': 'application/json'},
            'auth': (server_conf['user'], server_conf['password']),
            'data': post_json
        }
        response = requests.put(**put_kwargs)
        if response.status_code == 200:
            if response.json['error'] == 0:
                count = objects.update(deployed=True, user=user)
            else:
                raise ValueError(_('Error %(message)s with %(object)s' % response.json))
        else:
            raise ValueError(response.reason)
    return response, count
