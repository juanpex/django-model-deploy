# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from test_project import deploys

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^deploy/', include('model_deploy.urls')),
    url(r'^', include(admin.site.urls)),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
