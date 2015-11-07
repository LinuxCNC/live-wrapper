#!/usr/bin/env python

"""
live-build-ng - Live-Build NG
(C) Iain R. Learmonth 2015 <irl@debian.org>
See COPYING for terms of usage, modification and redistribution.

setup.py - setuptools script
"""

from setuptools import setup, find_packages

setup(
    name='live-build-ng',
    version='0.1',
    description='Create a Debian live image based on vmdebootstrap',
    author='Iain R. Learmonth',
    author_email='irl@debian.org',
    url='https://anonscm.debian.org/cgit/vmdebootstrap/live-build-ng.git/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: System :: Installation/Setup',
    ],
    packages=[
        'lbng',
    ],
    package_data={
        'live-build-ng': ['README', 'COPYING'],
    },
    install_requires=[
        'cliapp >= 1.20150829',
        'vmdebootstrap',
    ],
    scripts=['bin/lbng']
)
