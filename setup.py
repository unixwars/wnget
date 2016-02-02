#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from codecs import open
from os import path
import re

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
with open('wnget/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)
with open(path.join(here, 'requirements.txt')) as f:
    req_install = list(filter(None, f.readlines()))

setup(
    name='wnget',
    version=version,
    description='web novel getter, a web scraping and ebook generation tool.',
    long_description=long_description,
    url='https://github.com/unixwars/wnget',
    author='Taher Shihadeh',
    author_email='taher@unixwars.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Topic :: Documentation',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='webscraper epub ebook webnovel',
    setup_requires=['pytest-runner'] + req_install,
    tests_require=['pytest', 'tox'] + req_install,
    install_requires=req_install,
    packages=find_packages(exclude=['contrib', 'doc', 'test*']),
    package_dir={'wnget': 'wnget'},
    package_data={
        '': ['LICENSE', 'README.md'],
        'wnget': ['templates/*'],
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'wnget=wnget.main:wnget',
            'wnbook=wnget.main:wnbook',
        ],
    },
)
