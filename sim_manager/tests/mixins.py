# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
