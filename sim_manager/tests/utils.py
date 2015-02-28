# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase

from sim_manager.models import get_api_key


class ApiTestCase(ResourceTestCase):
    """
    Base class for API-related tests
    """
    ROOT_ENDPOINT = '/api/v1/'

    @classmethod
    def make_resource_uri(cls, *path_components):
        path_from_root_endpoint = '/'.join(str(x) for x in path_components)
        if len(path_from_root_endpoint) > 0 and path_from_root_endpoint[:-1] != '/':
            path_from_root_endpoint += '/'  # Make sure we have '/' at end
        full_path = cls.ROOT_ENDPOINT + path_from_root_endpoint
        return full_path


class TestsWithApiKeyAuth(ApiTestCase):
    """
    Base class representing tests that use API-key authentication.
    """
    # NOTE: User names should not contain spaces; they'll break API key authentication because the Authentication header
    #       is split into fields based on whitespace.
    TEST_USER_NAME = 'testuser'

    @classmethod
    def create_test_user(cls):
        """
        Create a user for test purposes.
        """
        cls.test_user = User.objects.create_user(TestsWithApiKeyAuth.TEST_USER_NAME)
        cls.test_user_api_key = get_api_key(cls.test_user)

    def get_credentials(self):
        """
        Get credentials for HTTP authorization header
        """
        return self.create_apikey(self.test_user.username, self.test_user_api_key)

    @classmethod
    def delete_test_user(cls):
        """
        Delete the test user.
        """
        cls.test_user.delete()
