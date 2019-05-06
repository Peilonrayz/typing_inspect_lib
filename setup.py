#!/usr/bin/env python
from setuptools import setup

VERSION = '0.0.1'
DESCRIPTION = 'Type inspections for Python'
LONG_DESCRIPTION = ''''''

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Topic :: Software Development',
]

INSTALL_REQUIRES = [
    'typing >= 3.6.1;python_version<"3.5"'
]

TEST_REQUIRES = []

EXTRA_REQUIRES = {
    'extensions': [
        'typing_extensions',
    ]
}

setup(
    name='typing_inspect_lib',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='Peilonrayz',
    author_email='peilonrayz@gmail.com',
    url='https://github.com/Peilonrayz/typing_inspect_lib',
    license='MIT',
    keywords='typing function annotations type hints hinting checking '
             'checker typehints typehinting typechecking inspect '
             'reflection introspection',
    py_modules=['typing_inspect'],
    classifiers=CLASSIFIERS,
    install_requires=INSTALL_REQUIRES,
    tests_require=TEST_REQUIRES,
    extras_require=EXTRA_REQUIRES,
    zip_safe=False  # todo: check if this package is zip-safe
)
