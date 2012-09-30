# -*- coding: utf-8 -*-
from model_deploy import core

from polls.models import Poll, Choice

core.register(Poll)
core.register(Choice)
