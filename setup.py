#!/usr/bin/env python

# live-wrapper - Wrapper for vmdebootstrap to create live images
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
# 
# setup.py - setuptools script

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'VERSION')) as version_file:
    version = version_file.read().strip()

setup(
    name='live-wrapper',
    version=version,
    description='Create a Debian live image based on vmdebootstrap',
    author='Iain R. Learmonth',
    author_email='irl@debian.org',
    url='https://anonscm.debian.org/cgit/debian-live/live-wrapper.git',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Installation/Setup',
    ],
    packages=[
        'lwr',
    ],
    package_data={
        'live-wrapper': ['README', 'COPYING'],
    },
    install_requires=[
        'cliapp >= 1.20150829',
        'vmdebootstrap',
        'requests',
        'python-apt'
    ],
    entry_points={
        'console_scripts': [
            'lwr = lwr.run:main',
        ],
    },
)
