# coding=utf-8
from setuptools import setup, find_packages

import lifelogger


setup(
    name='lifelogger',
    version=lifelogger.__version__,
    description=lifelogger.__doc__.strip(),
    long_description=open('README.md').read(),
    url='https://github.com/adamchainz/lifelogger',
    license=lifelogger.__license__,
    author=lifelogger.__author__,
    author_email='me@adamj.eu',
    packages=find_packages(),
    install_requires=open('requirements.txt').readlines(),
    entry_points={
        'console_scripts': [
            'lifelogger = lifelogger.main:main',
        ],
    },
    package_data={
        '': ['*.json'],
    },
)
