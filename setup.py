from setuptools import setup, find_packages

setup(
    name='PyOdyssey',
    version='0.1.0',
    author='Giuseppe Acito',
    author_email='giuseppe.acito@gmail.com',
    packages = find_packages(exclude=['test']),
    license = open('LICENSE.txt').read(),
    description = 'Client for Juniper Networks',
    long_description = open('README.md').read(),
    url = 'http://pypi.python.org/pypi/PyOdyssey/',
    install_requires = [
        "flypwd",
        "requests",
        "beautifulsoup4",
    ],
    entry_points={
        'console_scripts': [
           'pyodyssey = pyodyssey.core:main',
        ]
    },

    dependency_links=['https://github.com/giupo/flypwd/tarball/master#egg=flypwd']
)
