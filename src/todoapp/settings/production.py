import os

from .settings import *

DEBUG = False
PRODUCTION = True
SECRET_KEY = os.environ.get('SECRET_KEY')
