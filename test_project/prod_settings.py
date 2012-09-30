# -*- coding: utf-8 -*-
from settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dmd_prod.db'
    }
}

MEDIA_ROOT = PROJECT_ABSOLUTE_DIR + '/production/media/'

STATIC_ROOT = PROJECT_ABSOLUTE_DIR + '/production/static/'

MODEL_DEPLOY = False
