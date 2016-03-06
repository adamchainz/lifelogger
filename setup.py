# coding=utf-8
from setuptools import setup, find_packages

import lifelogger


setup(
    name='lifelogger',
    version=lifelogger.__version__,
    description=lifelogger.__doc__.strip(),
    long_description=open('README.rst').read(),
    url='https://github.com/adamchainz/lifelogger',
    license=lifelogger.__license__,
    author=lifelogger.__author__,
    author_email='me@adamj.eu',
    packages=find_packages(),
    install_requires=open('requirements.txt').readlines(),
    scripts=[
        'bin/lifelogger',
    ],
    package_data={
        '': ['*.json'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Office/Business :: Scheduling'
    ],
)
