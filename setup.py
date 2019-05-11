#!/usr/bin/env python
from setuptools import setup, find_packages

INSTALL_REQUIRES = [
    'typing >= 3.6.1;python_version<"3.5"'
]

TEST_REQUIRES = [
    'tox'
]

EXTRA_REQUIRES = {
    'extensions': [
        'typing_extensions',
    ]
}

setup(
    name='typing_inspect_lib',
    version='0.0.1',
    license='MIT',
    description='Type inspections for Python',
    long_description='''''',
    author='Peilonrayz',
    author_email='peilonrayz@gmail.com',
    url='https://github.com/Peilonrayz/typing_inspect_lib',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=['typing_inspect_lib'],
    include_package_data=True,
    zip_safe=False,  # todo: check if this package is zip-safe
    classifiers=[
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
    ],
    keywords='typing function annotations type hints hinting checking '
             'checker typehints typehinting typechecking inspect '
             'reflection introspection',
    install_requires=INSTALL_REQUIRES,
    tests_require=TEST_REQUIRES,
    extras_require=EXTRA_REQUIRES,
)
