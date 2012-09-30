# -*- coding: utf-8 -*-
from django import http
from django.contrib import admin
from django.contrib import messages
from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext_lazy as _

from model_deploy.utils import deploytoserver
from model_deploy.models import DeployObjectLog


def deploytoserver_action(modeladmin, request, queryset):
    for server in set(queryset.values_list('server', flat=True)):
        try:
            objects = queryset.filter(server=server)
            response, count = deploytoserver(objects, server, request.user)
            if response is None and count == 0:
                messages.error(request, _('There are no pending objects to publish in the %(server)s server' % {'server': server}))
                continue
            elif response and count == 0:
                messages.error(request, response.reason)
            elif response and count > 0:
                if response.status_code != 200:
                    messages.error(request, _('Error %(message)s with %(object)s' % response.json))
            else:
                raise ValueError('Unknown error')
            log = DeployObjectLog(server=server)
            messages.success(request, _('%(count)s objects was sent to %(server)s' % {'count': count, 'server': log.get_server_display()}))
        except Exception, e:
            messages.error(request, unicode(e))
deploytoserver_action.short_description = _('Deploy the selected objects to their target server')


def markasundeployed_action(modeladmin, request, queryset):
    queryset.update(deployed=False)
markasundeployed_action.short_description = _('Mark selected logs as undeployed')


def markasdeployed_action(modeladmin, request, queryset):
    queryset.update(deployed=True)
markasdeployed_action.short_description = _('Mark selected logs as deployed')


class DeployObjectLogAdmin(admin.ModelAdmin):
    list_display = ('server', 'content_type', 'action_time', 'action', 'object_id', 'object_repr', '_deploytoserver', 'deployed')
    list_filter = ('server', 'deployed', 'action', 'action_time')
    actions = [deploytoserver_action, markasdeployed_action, markasundeployed_action]

    def object_repr(self, obj):
        return unicode(obj.content_object)

    def _deploytoserver(self, obj):
        if not obj.deployed:
            output_vars = {
                'question': _('Are you sure?'),
                'pk': obj.pk,
                'value': _('Deploy to server'),
            }
            output = u'<input value="%(value)s" type="button" onclick=\'if(confirm("%(question)s")){window.location.href=window.location.pathname+"%(pk)s/deploy/";}\'/>'
            return output % output_vars
        else:
            return _('Deployed by "%(user)s"' % {'user': obj.user})
    _deploytoserver.short_description = _('Deployed?')
    _deploytoserver.allow_tags = True

    def get_urls(self):
        urls = super(DeployObjectLogAdmin, self).get_urls()
        urlpatterns = patterns('',
            url(r"^(?P<pk>\d+)/deploy/$", self.admin_site.admin_view(self.deploy_log)),
        )
        return urlpatterns + urls

    def deploy_log(self, request, pk):
        if not request.user.is_authenticated():
            return http.HttpResponseForbidden()
        deploytoserver_action(None, request, DeployObjectLog.objects.filter(pk=pk))
        return http.HttpResponseRedirect(request.META['HTTP_REFERER'])


admin.site.register(DeployObjectLog, DeployObjectLogAdmin)
