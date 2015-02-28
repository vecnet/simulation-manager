"""
Django settings for simulation manager project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import socket
import sys

from path import path


# Build paths inside the project like this: PROJECT_DIR / foo / bar.qux
PROJECT_ROOT = path(__file__).abspath().dirname().dirname()

# Are we running tests (./manage.py test ...) or the Django development server (./manage.py runserver ...)?
RUNNING_MANAGE_PY = 'manage.py' in sys.argv[0]

# For settings that are host (machine) specific
HOSTNAME = socket.gethostname().split('.', 1)[0]

try:
    from .secrets import *
except ImportError:
    pass


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sim_manager',
    'tastypie',
    'south',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'project.urls'

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': PROJECT_ROOT / 'db' / 'db.sqlite3',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'


TASTYPIE_DEFAULT_FORMATS = ['json']

# Where working directories for simulation groups are located
GROUP_WORKING_DIRS = PROJECT_ROOT / 'working-dirs' / 'sim-groups'

# Where working directories for individual simulations
SIMULATION_WORKING_DIRS = PROJECT_ROOT / 'working-dirs' / 'simulations'

# Path to the Python interpreter that's used to execute the command-line scripts.  For Apache/WSGI deployments, this
# will be different than the system Python.
if RUNNING_MANAGE_PY:
    PYTHON_FOR_SCRIPTS = sys.executable
else:
    host_python_executables = {
        'vecnet02': '/opt/sim_manager/venv/vecnet02/bin/python',
        'vecnet1': '/shared/sim_manager/venv/vecnet1/bin/python',
    }
    PYTHON_FOR_SCRIPTS = host_python_executables[HOSTNAME]


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'simple': {
            'format': '%(asctime)s | %(levelname)-7s | %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'sim_manager': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
