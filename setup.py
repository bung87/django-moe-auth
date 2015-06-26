#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import codecs
# import os
from distutils.core import setup

from setuptools import find_packages

# version_tuple = __import__('django_js_reverse').VERSION
# version = '.'.join([str(v) for v in version_tuple])
setup(
    name='django-moe-auth',
    version='0.0.1',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Framework :: Django',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
    ],
    license='MIT',
    description='Javascript url handling for Django that doesn\'t hurt.',
    # long_description=read('README.rst'),
    author='Bung',
    author_email='zh.bung@gmail.com',
    url='https://github.com/bung87/django-moe-auth',
    download_url='https://github.com/bung87/django-moe-auth',
    packages=find_packages(),

    install_requires=[
        'Django>=1.5',
        'mongoengine==0.8.8',
        'djangorestframework==3.0.5',
        'django-allauth>=0.19.1'
    ]
)
