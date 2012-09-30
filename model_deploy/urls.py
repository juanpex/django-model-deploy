# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('model_deploy.views',
    url(r"^$", 'deploy_data', name="deploy_data"),
)
