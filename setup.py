#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='oandata',
      version='0.1',
      description='A python wrapper for OANDA v20 API',
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
