# config/settings/local.py
from .dev import *

# Override any settings here
DATABASES['default']['NAME'] = 'test_local'
