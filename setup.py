import os
from distutils.sysconfig import get_python_lib
from shutil import copyfile
copyfile('pyWars.py', os.path.join(get_python_lib(), 'pyWars.py'))
