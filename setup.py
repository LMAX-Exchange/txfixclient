#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#

from setuptools.command.install import install
from setuptools import find_packages
from setuptools import setup


def refresh_plugin_cache():
    from twisted.plugin import IPlugin, getPlugins
    list(getPlugins(IPlugin))


def read(path):
    """
    Read the contents of a file.
    """
    with open(path) as f:
        return f.read()

if __name__ == '__main__':
    setup(
        name='txfixclient',
        version='0.1.0',
        description='FIX protocol performance monitoring tool',
        keywords='fix twisted performance',
        author='Tim Hughes',
        author_email='tim.hughes@lmax.com',
        url='https://github.com/lmax-exchange/txfixclient',
        package_dir={'': 'src'},
        packages=["txfixclient", "twisted.plugins"],
        package_data={
            'twisted': ['plugins/txfixclient_plugin.py'],
        },
        install_requires=[
            'Twisted>=16.0.0',
            'service_identity',
            'hdrhistogram',
            ],
        scripts=['src/scripts/txfixclient',],
        license="Apache-2.0",
        long_description=read('README.rst'),
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'Intended Audience :: Information Technology',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
        ],
        zip_safe=False
    )
