from urlparse import urlparse

from django.utils import timezone

from vecnet.simulation import ExecutionRequest, submission_status
from sim_manager import async, working_dirs
from sim_manager.api import SimulationGroupResource
from sim_manager.models import SimulationGroup
from sim_manager.tests.utils import TestsWithApiKeyAuth


class GroupApiTests(TestsWithApiKeyAuth):
    """
    Tests of the API for simulation groups.
    """

    @classmethod
    def setUpClass(cls):
        super(GroupApiTests, cls).setUpClass()
        cls.create_test_user()
        cls.group_endpoint = cls.make_resource_uri(SimulationGroupResource.Meta.resource_name)
        working_dirs.TestingApi.use_testing_root()
        cls.mock_start_task = async.TestingApi.disable_start_task()

    @classmethod
    def tearDownClass(cls):
        cls.delete_test_user()
        async.TestingApi.enable_start_task()
        working_dirs.TestingApi.reset_root_to_default()

    def test_get_list_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.get(self.group_endpoint))

    def test_post_list_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.post(self.group_endpoint))

    def test_post_list_invalid_json(self):
        invalid_json = '{ "foo": }'  # Missing value for key

        # In order to have the "data" parameter treated as a string and not as a dictionary, we have to use the Django
        # test client rather than the Tastypie's test client.  Furthermore, we have to give that client an explicit
        # content_type.
        self.assertHttpBadRequest(self.client.post(self.group_endpoint, content_type='application/json',
                                                   data=invalid_json, HTTP_AUTHORIZATION=self.get_credentials()))

    def test_post_list(self):
        count_before_post = SimulationGroup.objects.count()
        datetime_before_post = timezone.now()
        process_id = 98765
        self.mock_start_task.reset_mock()
        self.mock_start_task.return_value = process_id

        execution_request = ExecutionRequest()
        resp = self.api_client.post(self.group_endpoint, data=execution_request.to_dict(),
                                    authentication=self.get_credentials())
        self.assertHttpCreated(resp)

        # Check that the Location header points to the new group
        group_url = urlparse(resp['Location'])
        self.assertTrue(group_url.path.startswith(self.group_endpoint))
        path_from_endpoint = group_url.path[len(self.group_endpoint):]
        self.assertRegexpMatches(path_from_endpoint, r'^\d+/$')  # Check for the new group's id at end of URL

        # Check that a group was created
        self.assertEqual(SimulationGroup.objects.count(), count_before_post + 1)
        group_id = path_from_endpoint.rstrip('/')
        group = SimulationGroup.objects.get(id=group_id)
        self.assertEqual(group.submitter, self.test_user)
        self.assertLessEqual(datetime_before_post, group.submitted_when)
        self.assertEqual(group.script_status, submission_status.READY_TO_RUN)

        # Check if the submission script was started successfully
        self.assertTrue(self.mock_start_task.called)
        self.assertEqual(self.mock_start_task.call_count, 1)
        self.assertEqual(group.process_id, process_id)

    def test_post_list_empty_execution_request(self):
        execution_request = {
        }
        resp = self.api_client.post(self.group_endpoint, data=execution_request, authentication=self.get_credentials())
        self.assertHttpBadRequest(resp)

        error_info = self.deserialize(resp)
        self.assertKeys(error_info, ['error', 'error_details'])
        self.assertIsInstance(error_info['error'], basestring)
        expected_details = {
            'missing_key': 'simulation_group',
            'class': 'ExecutionRequest'
        }
        self.assertEqual(error_info['error_details'], expected_details)

    def test_patch_status(self):
        group = SimulationGroup.objects.create(submitter=self.test_user)
        new_status = submission_status.SUBMITTING_JOBS
        resp = self.api_client.patch('%s%s/' % (self.group_endpoint, group.id), data=dict(script_status=new_status),
                                     authentication=self.get_credentials())
        self.assertHttpAccepted(resp)
        group = SimulationGroup.objects.get(id=group.id)  # Reload the model instance
        self.assertEqual(group.script_status, new_status)

    def test_patch_restricted_field(self):
        group = SimulationGroup.objects.create(submitter=self.test_user)
        bad_data = {
            'process_id': -5,  # Not allowed to change this field
        }
        resp = self.api_client.patch('%s%s/' % (self.group_endpoint, group.id), data=bad_data,
                                     authentication=self.get_credentials())
        self.assertHttpBadRequest(resp)
