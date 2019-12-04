#!/usr/bin/env python
from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='public_meetings',
    description='A corpus of public meetings',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='0.1.0rc3',
    packages=find_packages(),
    project_urls={
        "Documentation": "http://github.com/pltrdy/public_meetings",
        "Source": "https://github.com/pltrdy/public_meetings"
    },
    install_requires=[
        "numpy",
    ],
    package_data={
        'public_meetings': [
            'data/*.aligned.pckl',
            'data/*.docx',
            'data/*.ctm',
        ],
    },
    entry_points={
        "console_scripts": [
            "public_meetings=public_meetings.bin.commands:main",
        ],
    }
)
