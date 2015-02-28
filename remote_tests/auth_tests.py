import unittest

import requests

from conf import Api, Settings


class AuthenticationTests(unittest.TestCase):
    """
    Tests of the API-key authentication.
    """
    def test_squares_unauthenticated(self):
        number = -6
        resource_path = Api.make_full_url_path('squares', number)
        resource_url = Api.make_url(resource_path)
        resp = requests.get(resource_url)
        self.assertEqual(resp.status_code, 401)

    def test_squares(self):
        number = 3
        resource_path = Api.make_full_url_path('squares', number)
        resource_url = Api.make_url(resource_path)

        username = Settings.user
        api_key = Settings.api_key
        headers = {
            'Authorization': "ApiKey %s:%s" % (username, api_key),
        }

        resp = requests.get(resource_url, headers=headers)
        self.assertEqual(resp.status_code, 200)
        expected_json = {
            'number': number,
            'square': number * number,
            'resource_uri': resource_path,
        }
        self.assertEqual(resp.json(), expected_json)
