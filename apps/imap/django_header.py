"""
This stub is necessary to make standalone applications that use the brightmap django 
environment in order to work with the databases
"""

import sys
from datetime                   import datetime
from os.path                    import abspath, dirname, join,split
from site                       import addsitedir

# Set up the environment to run on it own.
APP_ROOT, tail = split(abspath(dirname(__file__)))
PROJECT_ROOT, tail = split(APP_ROOT)

sys.path.insert(0,PROJECT_ROOT)
sys.path.insert(0,APP_ROOT)

from django.core.management     import setup_environ

import settings
setup_environ(settings)
