#!/usr/bin/env python

from distutils.core import setup

import os
execfile(os.path.join('pagerduty', 'version.py'))

try:
    long_description = open("README.md").read()
except IOError:
    long_description = ""

setup(
    name = 'pagerduty',
    version = VERSION,
    description = 'Library for the PagerDuty service API',
    long_description = long_description,
    author = 'Samuel Stauffer',
    author_email = 'samuel@playhaven.com',
    url = 'http://github.com/samuel/python-pagerduty',
    packages = ['pagerduty'],
    license = "BSD",
    entry_points = {
        "console_scripts": [
            "pagerduty = pagerduty.command:main",
        ],
    },
    classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
