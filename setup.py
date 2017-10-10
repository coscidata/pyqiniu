# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

version = '0.0.1'

setup(
    name='pyqiniu',
    version=version,
    description="",
    long_description=open("README.md").read(),
    classifiers=[],
    keywords='',
    author='',
    author_email='',
    license='Coscidata',
    packages=find_packages(exclude=['ez_setup', 'examples*', 'tests*']),
    include_package_data=True,
    install_requires=['requests'],
    zip_safe=False)
