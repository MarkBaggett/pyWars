import os
from distutils.sysconfig import get_python_lib
from shutil import copyfile
from setuptools import setup
copyfile('pyWars.py', os.path.join(get_python_lib(), 'pyWars.py'))
setup(install_requires = ["requests >=2.20.0"])

