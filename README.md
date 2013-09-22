Django Model Deploy
===================

Django application that facilitates the publication of data between environments such as development, testing and production.


Installation
============

* Add the ``model_deploy`` directory to your Python path.

* Add ``model_deploy`` to your ``INSTALLED_APPS`` setting.

* Create file "deploys.py" within the project directory.

* Edit the file "deploys.py" and register your models to be deployed like this:

        from app.models import AppModel
        from model_deploy import core

        core.register(AppModel)

* In your urls.py import your module "deploys.py".

        from projectfolder import deploys


Configuration
=============

* ``SERVERS``

    A dictionary, like ``DATABASES``, when you describe the environments for each server you have.
    For example::

        SERVERS = {
            'current': {
                'name': 'Testing server',
                'url': 'http://127.0.0.1:8000',
                'user': 'admin',
                'password': 'admin'
            },
            'production': {
                'name': 'Production server',
                'url': 'http://127.0.0.1:8001/deploy/',
                'user': 'padmin',
                'password': 'padmin'
            },
        }
   ``'name'``: Friendly name of the server.

   ``'url'``: URL of the server that is configured to handle ``model_deploy`` logs sent.

   ``'user'`` and ``'password'``: valid user credentials of ``django.contrib.auth``.



* Optional: ``DEFAULT_DEPLOY_SERVER`` Default: ``None``.

      Key value of the server to target all logs to deploy.

      For example:: ``'production'``



* Optional: ``MODEL_DEPLOY`` Default: ``True``.

      This setting manages the generation of logs changes made to the data of registered models.

      Is you must set to False when the project is not required to send data to another server.


Usage
=====

You can manage your deploys with ``django.contrib.admin`` or running ``./manage.py deploytoserver --server=serverkey``


Demo
====

Clone the repository and runs on two separate consoles:

1 $ ./manage.py runserver 8000

2 $ ./prod_manage.py runserver 8001


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/juanpex/django-model-deploy/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

