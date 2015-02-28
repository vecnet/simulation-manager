from urlparse import urlparse

from django.utils import timezone
from vecnet.simulation import sim_status

from sim_manager import working_dirs
from sim_manager.api import SimulationGroupResource, SimulationResource
from sim_manager.models import Simulation, SimulationGroup
from sim_manager.tests.utils import TestsWithApiKeyAuth


class SimulationApiTests(TestsWithApiKeyAuth):
    """
    Tests of the API for individual simulations.
    """

    @classmethod
    def setUpClass(cls):
        super(SimulationApiTests, cls).setUpClass()
        working_dirs.TestingApi.use_testing_root()
        cls.create_test_user()
        cls.simulations_endpoint = cls.make_resource_uri(SimulationResource.Meta.resource_name)

        cls.sim_group = SimulationGroup.objects.create(submitter=cls.test_user)
        cls.sim_group_uri = SimulationGroupResource().get_resource_uri(cls.sim_group)

    @classmethod
    def tearDownClass(cls):
        cls.delete_test_user()
        working_dirs.TestingApi.reset_root_to_default()

    def test_get_list_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.get(self.simulations_endpoint))

    def test_get(self):
        simulation = Simulation.objects.create(group=self.sim_group)
        simulation_uri = self.simulations_endpoint + '%s/' % simulation.id

        resp = self.api_client.get(simulation_uri, authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)

        data = self.deserialize(resp)
        expected_data = {
            'id': simulation.id,
            'created_when': simulation.created_when.strftime('%Y-%m-%dT%H:%M:%S.%f'),  # No timezone included in resp
            'resource_uri': simulation_uri,
            'group': self.sim_group_uri,
            'batch_job_id': '',
            'status': sim_status.READY_TO_RUN,
            'id_on_client': '',
            'error_details': '',
        }
        self.assertEqual(data, expected_data)

    def test_post_list_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.post(self.simulations_endpoint))

    def test_post_list_invalid_json(self):
        invalid_json = '{ "foo": }'  # Missing value for key

        # In order to have the "data" parameter treated as a string and not as a dictionary, we have to use the Django
        # test client rather than the Tastypie's test client.  Furthermore, we have to give that client an explicit
        # content_type.
        self.assertHttpBadRequest(self.client.post(self.simulations_endpoint, content_type='application/json',
                                                   data=invalid_json, HTTP_AUTHORIZATION=self.get_credentials()))

    def test_post_list(self):
        count_before_post = Simulation.objects.count()
        datetime_before_post = timezone.now()
        id_on_client = '123'

        resp = self.api_client.post(self.simulations_endpoint,
                                    data=dict(group=self.sim_group_uri,
                                              id_on_client=id_on_client),
                                    authentication=self.get_credentials())
        self.assertHttpCreated(resp)

        # Check that the Location header points to the new simulation
        simulation_url = urlparse(resp['Location'])
        self.assertTrue(simulation_url.path.startswith(self.simulations_endpoint))
        path_from_endpoint = simulation_url.path[len(self.simulations_endpoint):]
        self.assertRegexpMatches(path_from_endpoint, r'^\d+/$')  # Check for the new simulation's id at end of URL

        # Check that a simulation was created
        self.assertEqual(Simulation.objects.count(), count_before_post + 1)
        simulation_id = path_from_endpoint.rstrip('/')
        simulation = Simulation.objects.get(id=simulation_id)
        self.assertLessEqual(datetime_before_post, simulation.created_when)
        self.assertEqual(simulation.group.id, self.sim_group.id)
        self.assertEqual(simulation.id_on_client, id_on_client)

        # Check working directory in the response
        resp_data = self.deserialize(resp)
        self.assertEqual(resp_data['working_dir'], simulation.working_dir)

    def test_patch_batch_job(self):
        simulation = Simulation.objects.create(group=self.sim_group)
        self.assertEqual(simulation.batch_job_id, '')

        job_id = '10987'
        resp = self.api_client.patch('%s%s/' % (self.simulations_endpoint, simulation.id),
                                     data=dict(batch_job_id=job_id),
                                     authentication=self.get_credentials())
        self.assertHttpAccepted(resp)
        simulation = Simulation.objects.get(id=simulation.id)  # Reload the model instance
        self.assertEqual(simulation.batch_job_id, job_id)

    def test_patch_restricted_field(self):
        simulation = Simulation.objects.create(group=self.sim_group)
        bad_data = {
            'created_when': timezone.now(),  # Not allowed to change this field
        }
        resp = self.api_client.patch('%s%s/' % (self.simulations_endpoint, simulation.id), data=bad_data,
                                     authentication=self.get_credentials())
        self.assertHttpBadRequest(resp)
