#!/usr/bin/env python3
"""
@Filename:    setup.py.py
@Author:      dulanj
@Time:        02/02/2022 01:53
"""
from setuptools import setup, find_packages

import sports_event_detection

setup(
    name='sports_event_detection',
    version=sports_event_detection.__version__,
    description='Sports Events Detection and Recognition',
    url='https://www.something.com/',
    author='Dulan Jayasuriya',
    author_email='dulan.20@cse.mrt.ac.lk',
    license='Proprietary',
    packages=find_packages(),
    zip_safe=False
)
