#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='oandata',
      version='0.2',
      description='A python wrapper for OANDA v20 API',
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
      ],
      keywords='oanda price-data',
      url='http://github.com/hhatefi/oandata',
      author='Hassan Hatefi',
      author_email='hhatefi@gmail.com',
      license='MIT',
      packages=['oandata'],
      install_requires=['v20', 'pandas'],
      entry_points = {'console_scripts': ['fetch_oandata=fetch_oandata:main']},
      include_package_data=True,
      zip_safe=False)
