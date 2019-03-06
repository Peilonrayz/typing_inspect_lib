#!/usr/bin/env python
from setuptools import setup

version = '0.0.1'
description = 'Type inspections for Python'
long_description = ''''''

classifiers = [
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

install_requires = [
    'typing >= 3.6.1;python_version<"3.5"'
]

test_requires = []

extra_requires = {
    'extensions': [
        'typing_extensions',
    ]
}

setup(
    name='typing_inspect_lib',
    version=version,
    description=description,
    long_description=long_description,
    author='Peilonrayz',
    author_email='peilonrayz@gmail.com',
    url='https://github.com/Peilonrayz/typing_inspect_lib',
    license='MIT',
    keywords='typing function annotations type hints hinting checking '
             'checker typehints typehinting typechecking inspect '
             'reflection introspection',
    py_modules=['typing_inspect'],
    classifiers=classifiers,
    install_requires=install_requires,
    tests_require=test_requires,
    extras_require=extra_requires,
)
