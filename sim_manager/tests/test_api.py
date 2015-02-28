from sim_manager import api
from sim_manager.tests.utils import ApiTestCase, TestsWithApiKeyAuth


class ApiTests(ApiTestCase):
    """
    Tests for the API.
    """
    def make_resource_info(self, resource):
        """
        Make a dictionary with information about a resource's list endpoint and schema.
        """
        resource_name = resource.Meta.resource_name
        resource_list_endpoint = self.make_resource_uri(resource_name)
        schema_uri = self.make_resource_uri(resource_name, 'schema')
        return {
            'list_endpoint': resource_list_endpoint,
            'schema': schema_uri,
        }

    def test_main_endpoint_json(self):
        """
        Test that the API's main endpoint returns information about known endpoints.
        """
        resp = self.api_client.get(self.ROOT_ENDPOINT)
        self.assertValidJSONResponse(resp)

        expected_data = {}
        for resource in api.RESOURCES:
            resource_name = resource.Meta.resource_name
            resource_info = self.make_resource_info(resource)
            expected_data[resource_name] = resource_info

        resp_data = self.deserialize(resp)
        self.assertEqual(resp_data, expected_data)


class AuthenticationTests(TestsWithApiKeyAuth):
    """
    Tests for authentication using API keys.
    """

    @classmethod
    def setUpClass(cls):
        super(AuthenticationTests, cls).setUpClass()
        cls.create_test_user()

    @classmethod
    def tearDownClass(cls):
        cls.delete_test_user()

    def test_squares_get_list(self):
        squares_endpoint = self.make_resource_uri('squares')
        self.assertHttpMethodNotAllowed(self.api_client.get(squares_endpoint))

    def test_squares_unauthorzied(self):
        squares_schema_uri = self.make_resource_uri('squares', 'schema')
        self.assertHttpUnauthorized(self.api_client.get(squares_schema_uri))

    def test_squares_get_detail(self):
        number = 6
        detail_uri = self.make_resource_uri('squares', number)
        resp = self.api_client.get(detail_uri, authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
        data = self.deserialize(resp)
        self.assertDictEqual(data, {
            'number': number,
            'resource_uri': detail_uri,
            'square': number * number,
        })
