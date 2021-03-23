import os
from distutils.sysconfig import get_python_lib
from shutil import copyfile
from setuptools import setup
copyfile('pyWars.py', os.path.join(get_python_lib(), 'pyWars.py'))
setup(
    name="pywars", 
    version="4.0.1", 
    install_requires = ["requests >= 2.20.0", "rich >= 9.1.0"],
    license="All Rights Reserved. Do not distribute.",
    url="https://github.com/markbaggett/pyWars"
    )

