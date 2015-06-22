from .common import *
import os

os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = 'localhost:8005-8010,8080,9200-9300'

DEBUG = True

TEMPLATE_DEBUG = True

SECRET_KEY = '1af!9it2i$z&k+2@)+xcfq7)m4urd+y70&u1d@ci+5)6x!505^'
