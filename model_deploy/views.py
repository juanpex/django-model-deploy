# -*- coding: utf-8 -*-
import base64

from django import http
from django.db import transaction
from django.utils import simplejson
from django.db import DEFAULT_DB_ALIAS
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType

from model_deploy.models import DeleteObject
from model_deploy.serializer import Deserializer


@csrf_exempt
@transaction.commit_manually
def deploy_data(request):
    response = http.HttpResponse()
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'PUT, POST, GET, OPTIONS'
    response['Access-Control-Max-Age'] = 1000
    response['Access-Control-Allow-Headers'] = 'Authorization, X-CSRFToken'

    if request.method == 'OPTIONS':
        return response
    if request.method != 'PUT':
        return http.HttpResponseNotAllowed()

    if not request.META.get('HTTP_AUTHORIZATION'):
        return http.HttpResponseForbidden()

    try:
        (auth_type, data) = request.META['HTTP_AUTHORIZATION'].split()
        if auth_type.lower() != 'basic':
            return http.HttpResponseForbidden()
        user_pass = base64.b64decode(data)
    except:
        return http.HttpResponseForbidden()

    bits = user_pass.split(':', 1)

    if len(bits) != 2:
        return http.HttpResponseBadRequest()

    user = authenticate(username=bits[0], password=bits[1])
    if not user or not user.is_active:
        return http.HttpResponseForbidden()

    try:
        for obj in Deserializer(request.raw_post_data, using=DEFAULT_DB_ALIAS):
            if isinstance(obj.object, DeleteObject):
                ct = ContentType.objects.get_by_natural_key(obj.object.app_label, obj.object.model)
                ct.model_class().objects.get(pk=obj.object.pk).delete()
            else:
                obj.save()
            transaction.commit()
        response = {'message': 'OK', 'error': 0, 'object': None}
    except Exception, e:
        transaction.rollback()
        response = {'message': unicode(e), 'error': 1, 'object': unicode(obj.object)}
    return http.HttpResponse(simplejson.dumps(response), content_type='text/json')
