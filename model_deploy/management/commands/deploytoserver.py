# -*- coding: utf-8 -*-
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from model_deploy.models import DeployObjectLog
from model_deploy.utils import deploytoserver


class Command(BaseCommand):
    help = 'This command helps to deploys objects to server by console.'

    option_list = BaseCommand.option_list + (
        make_option('--server', action='store', dest='server',
                    default=None, help='Server key'),
    )

    requires_model_validation = False

    def handle(self, **options):
        SERVERS = getattr(settings, 'SERVERS', {})

        if not SERVERS:
            raise CommandError('There are no SERVERS in your settings file')

        server = options.get('server', None)

        if not server:
            raise CommandError('Provide a server key.')

        if not server in SERVERS:
            raise CommandError('Server key "%(server)s" does not exist in your settings.' % {'server': server})

        objects = DeployObjectLog.objects.filter(deployed=False, server=server)
        try:
            response, count = deploytoserver(objects, server)
            if response is None and count == 0:
                print 'There are no pending objects to publish in the %(server)s server' % {'server': server}
                return
            elif count > 0 and response:
                if response.status_code != 200:
                    print 'Error %(message)s with %(object)s' % response.json
            elif response:
                print response.reason
            else:
                raise ValueError('Unknown error')
        except Exception, e:
            raise CommandError(unicode(e))
