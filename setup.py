#!/usr/bin/env python

import setuptools

__version__ = '0.3.0'

# Define the project's long description by reading from the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Short description of your library
short_description = 'Kudi: An open-source Python library for the analysis of properties along reaction paths.'

# Define the list of requirements for your project
required_packages = [
    'numpy',
    'scipy',
    'matplotlib',
    # Add other dependencies here
]

# Setup function
setuptools.setup(
    name='kudi',  # Replace with your own package's name
    version=__version__,
    author='Stefan Vogt',
    author_email='stvogtgeisse@qcmmlab.com',
    description=short_description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/stvogt/kudi',
    project_urls={
        "Bug Tracker": "https://github.com/stvogt/kudi/issues",
        # Add other project URLs here (Documentation, FAQ, etc.)
    },
    classifiers=[
        # Choose your license as you wish
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        # Add other Python versions you support
    ],
    packages=setuptools.find_packages(),  # Automatically find packages
    python_requires=">=3.8",  # Specify the minimum Python version required
    install_requires=required_packages,
    # Uncomment the following if you have defined entry points
    # entry_points={
    #     'console_scripts': ['your_script_name=your_package.your_module:main_function']
    # },
)

