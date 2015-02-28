import json
import time
import unittest
from urlparse import urlparse

import requests
from vecnet.simulation import ExecutionRequest, sim_model, Simulation, SimulationGroup, sim_status, submission_status

from conf import Api, Settings


class MockSimulationModelTests(unittest.TestCase):
    """
    Tests with the Mock simulation model
    """

    @classmethod
    def setUpClass(cls):
        super(MockSimulationModelTests, cls).setUpClass()

        cls.groups_endpoint_path = Api.make_full_url_path('sim-groups')
        cls.groups_endpoint_url = Api.make_url(cls.groups_endpoint_path)

        username = Settings.user
        api_key = Settings.api_key
        cls.headers = {
            'Authorization': "ApiKey %s:%s" % (username, api_key),
            'Content-type': "application/json",
        }

    def submit_group(self, execution_request):
        """
        Posts an execution request for a simulation group, and asserts that the group was created.

        ":return:" Id of the new group
        """
        request_data = json.dumps(execution_request.to_dict())
        resp = requests.post(self.groups_endpoint_url, data=request_data, headers=self.headers)
        self.assertEqual(resp.status_code, 201)

        location = resp.headers['Location']
        self.assertTrue(location.startswith(self.groups_endpoint_url))
        group_url = urlparse(location)
        path_from_endpoint = group_url.path[len(self.groups_endpoint_path):]
        self.assertRegexpMatches(path_from_endpoint, r'^\d+/$')  # Check for the new group's id at end of URL

        group_id = int(path_from_endpoint.rstrip('/'))
        return group_id

    def wait_for_status(self, resource_url, status_field, expected_statuses):
        """
        Waits for a resource's status to change to one of the values in a given list.

        :param resource_url: URL of the REST resource to query with a GET request.
        :param status_field: Name of the status field in the resource
        :param expected_statuses: List of statuses that will stop the wait.
        """
        MAX_WAIT_TIME = 3  # Seconds
        QUERY_INTERVAL = 0.2 # Seconds between queries
        time_waited = 0
        while time_waited <= MAX_WAIT_TIME:
            resp = requests.get(resource_url, headers=self.headers)
            self.assertEqual(resp.status_code, 200)
            resource_status = resp.json()[status_field]
            if resource_status in expected_statuses:
                return resource_status
            time.sleep(QUERY_INTERVAL)
            time_waited += QUERY_INTERVAL

    def get_simulations(self, group_id):
        """
        Gets the simulations for a group by querying the server.
        """
        group_resource_path = self.groups_endpoint_path + '{}/'.format(group_id)
        group_url = Api.make_url(group_resource_path)
        self.wait_for_status(group_url, 'script_status',
                             (submission_status.SCRIPT_DONE, submission_status.SCRIPT_ERROR))

        simulations_endpoint_path = Api.make_full_url_path('simulations')
        simulations_endpoint_url = Api.make_url(simulations_endpoint_path)

        query_url = simulations_endpoint_url + '?group={}'.format(group_id)
        resp = requests.get(query_url, headers=self.headers)
        self.assertEqual(resp.status_code, 200)

        json_content = resp.json()
        if json_content['meta']['total_count'] == 0:
            return []
        else:
            simulations = json_content['objects']
            for simulation in simulations:
                self.assertEqual(simulation['group'], group_resource_path)
            return simulations

    def wait_for_simulation_stop(self, resource_path):
        """
        Waits until a simulation stops (either it finishes or errors out).
        """
        simulation_url = Api.make_url(resource_path)
        status = self.wait_for_status(simulation_url, 'status', (sim_status.SCRIPT_DONE, sim_status.SCRIPT_ERROR))
        return status

    def test_no_input(self):
        """
        Test with no input files.
        """
        simulation = Simulation(model=sim_model.MOCK, model_version='0.1', id_on_client='43')
        sim_group = SimulationGroup(simulations=[simulation])
        execution_request = ExecutionRequest(simulation_group=sim_group)

        group_id = self.submit_group(execution_request)

        # Confirm that the group has one simulation
        simulations = self.get_simulations(group_id)
        self.assertEqual(len(simulations), 1)

        # Confirm that the simulation completed successfully.
        simulation = simulations[0]
        simulation_status = self.wait_for_simulation_stop(simulation['resource_uri'])
        self.assertEqual(simulation_status, sim_status.SCRIPT_DONE)

    def test_bad_input_url(self):
        """
        Test with an input file whose URL has a bad scheme.
        """
        simulation = Simulation(model=sim_model.MOCK, model_version='0.1', id_on_client='4')
        bad_url = 'BAD://UNKNOWNHOST.vecnet.org/path/to/non-existent-file.txt'
        simulation.input_files['input_file.txt'] = bad_url
        sim_group = SimulationGroup(simulations=[simulation])
        execution_request = ExecutionRequest(simulation_group=sim_group)

        group_id = self.submit_group(execution_request)

        # Confirm that the group has one simulation
        simulations = self.get_simulations(group_id)
        self.assertEqual(len(simulations), 1)

        simulation = simulations[0]
        simulation_status = self.wait_for_simulation_stop(simulation['resource_uri'])
        self.assertEqual(simulation_status, sim_status.SCRIPT_ERROR)
