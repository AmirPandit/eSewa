# config/settings/dev.py
from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Use SQLite or simple PostgreSQL for dev
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.getenv("DB_NAME", "your_db_name"),
#         'USER': os.getenv("DB_USER", "postgres"),
#         'PASSWORD': os.getenv("DB_PASSWORD", "postgres"),
#         'HOST': os.getenv("DB_HOST", "localhost"),
#         'PORT': os.getenv("DB_PORT", "5432"),
#     }
# }
