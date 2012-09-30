#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import join, dirname
from setuptools import setup


version = __import__('model_deploy').__version__


LONG_DESCRIPTION = """
Django Model Deploy
===================

Django application that facilitates the publication of data between environments such as development, testing and production.

    $ git clone git://github.com/juanpex/django-model-deploy.git
"""


def long_description():
    try:
        return open(join(dirname(__file__), 'README.md')).read()
    except IOError:
        return LONG_DESCRIPTION


setup(name='django-model-deploy',
      version=version,
      author='juanpex',
      author_email='jpma55@gmail.com',
      description='Django application that facilitates the publication of data between environments such as development, testing and production.',
      download_url='https://github.com/juanpex/django-model-deploy/zipball/master/',
      license='BSD',
      keywords='django, model, deploy, development, testing, production',
      url='https://github.com/juanpex/django-model-deploy',
      packages=['model_deploy', ],
      package_data={'model_deploy': ['locale/*/LC_MESSAGES/*']},
      long_description=long_description(),
      install_requires=['django>=1.4', ],
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ])
