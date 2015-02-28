"""
Mixin classes for test suites.
"""

from django.contrib.auth.models import User
from django.test import TestCase

from sim_manager.models import get_api_key
from sim_manager.scripts import database_api


class UsesDatabaseApi(TestCase):
    """
    Tests that use the database_api module.
    """

    @classmethod
    def setup_database_api_user(cls):
        """
        Creates a test user and initializes the database_api module to use that user's credentials.
        """
        cls.test_user = User.objects.create_user('test-user')
        cls.api_key = get_api_key(cls.test_user)
        database_api.TestingApi.set_credentials(cls.test_user.username, cls.api_key)

    @classmethod
    def remove_database_api_user(cls):
        """
        Remove the test user and clear its credentials from the database_api module.
        """
        database_api.TestingApi.clear_credentials()
        del cls.api_key
        cls.test_user.delete()
        del cls.test_user
