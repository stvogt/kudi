#!/usr/bin/env python

import setuptools
import os

__version__ = '0.3.0'

# Find the absolute path
here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

short_description = 'Kudi: An open-source python library for the analysis of properties along reaction paths.'

setuptools.setup(
    name='kudi',
    version=__version__,
    maintainer='Stefan Vogt',
    maintainer_email='stvogtgeisse@gmail.com',
    description=short_description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/stvogt/kudi',
    license='MIT',
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
    ],
    packages=setuptools.find_packages(),  # Automatically find packages
    # Uncomment the following if you have entry points
    # entry_points={
    #     'console_scripts': ['your_script_name=your_package.your_module:main_function']
    # },
)

