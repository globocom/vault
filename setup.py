# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

VERSION = __import__('vault').__version__

setup(
    name='vault',
    version=VERSION,
    description='Admin webapp for OpenStack Keystone and OpenStack Swift.',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    author='Storm',
    author_email='storm@g.globo',
    url='https://github.com/globocom/vault',
    install_requires=[
        'Babel==2.3.4',
        'gunicorn==19.3.0',
        'Django==3.1.6',
        'django3-all-access==0.10.0',
        'iso8601==0.1.11',
        'mysqlclient==1.4.6',
        'netaddr==0.7.18',
        'oslo.config==5.2.0',
        'python-dateutil==2.5.3',
        'python-keystoneclient==3.16.0',
        'python-swiftclient==3.7.1',
        'pytz==2015.4',
        'requests==2.19.1',
        'cryptography==2.9.2'
    ],
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
)
