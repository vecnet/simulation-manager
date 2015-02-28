# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Tests for the scripts/database_api module.
"""

from urlparse import urlparse

from django.test import LiveServerTestCase
from vecnet.simulation import sim_status, submission_status

from sim_manager import working_dirs
from sim_manager.models import Simulation, SimulationGroup
from sim_manager.scripts import database_api
from sim_manager.tests.mixins import UsesDatabaseApi


class GroupRecordTests(LiveServerTestCase, UsesDatabaseApi):
    """
    Tests for the GroupRecord class.
    """

    @classmethod
    def setUpClass(cls):
        super(GroupRecordTests, cls).setUpClass()
        cls.setup_database_api_user()
        working_dirs.TestingApi.use_testing_root()

    @classmethod
    def tearDownClass(cls):
        cls.remove_database_api_user()
        working_dirs.TestingApi.reset_root_to_default()

    def test_update_script_status(self):
        group = SimulationGroup.objects.create(submitter=self.test_user)
        self.assertEqual(group.script_status, submission_status.READY_TO_RUN)

        group_url = self.live_server_url + ('/api/v1/sim-groups/%s/' % group.id)
        group_db_rec = database_api.get_group_record(group_url, '(not used for this test)')

        for new_status in (submission_status.STARTED_SCRIPT,
                           submission_status.CACHING_FILES,
                           submission_status.SUBMITTING_JOBS,
                           submission_status.SCRIPT_DONE,
                           submission_status.SCRIPT_ERROR):
            group_db_rec.update_script_status(new_status)
            group = SimulationGroup.objects.get(id=group.id)
            self.assertEqual(group.script_status, new_status)

    def test_add_new_simulation(self):
        group = SimulationGroup.objects.create(submitter=self.test_user)

        group_url = self.live_server_url + ('/api/v1/sim-groups/%s/' % group.id)
        simulations_endpoint = '/api/v1/simulations/'
        simulations_url = self.live_server_url + simulations_endpoint
        group_db_rec = database_api.get_group_record(group_url, simulations_url)

        id_on_client = 'hi!'
        simulation_db_rec, working_dir = group_db_rec.add_new_simulation(id_on_client=id_on_client)
        parsed_url = urlparse(simulation_db_rec.url)
        self.assertTrue(parsed_url.path.startswith(simulations_endpoint))
        path_after_endpoint = parsed_url.path.replace(simulations_endpoint, '')
        self.assertRegexpMatches(path_after_endpoint, r'^\d+/$')
        id_in_url = path_after_endpoint.replace('/', '')

        # Check that a simulation was added to the group
        self.assertEqual(group.simulation_set.count(), 1)
        simulation = group.simulation_set.first()
        self.assertEqual(simulation.id, int(id_in_url))
        self.assertEqual(simulation.working_dir, working_dir)
        self.assertEqual(simulation.id_on_client, id_on_client)


class SimulationRecordTests(LiveServerTestCase, UsesDatabaseApi):
    """
    Tests for the SimulationRecord class.
    """

    @classmethod
    def setUpClass(cls):
        super(SimulationRecordTests, cls).setUpClass()
        cls.setup_database_api_user()
        working_dirs.TestingApi.use_testing_root()
        cls.group = SimulationGroup.objects.create(submitter=cls.test_user)

    @classmethod
    def tearDownClass(cls):
        cls.remove_database_api_user()
        working_dirs.TestingApi.reset_root_to_default()

    def test_set_batch_job(self):
        simulation = Simulation.objects.create(group=self.group)
        self.assertEqual(simulation.batch_job_id, '')

        simulation_url = self.live_server_url + ('/api/v1/simulations/%s/' % simulation.id)
        simulation_db_rec = database_api.get_simulation_record(simulation_url)
        job_id = 'host.6420'
        simulation_db_rec.set_batch_job(job_id)
        simulation = Simulation.objects.get(id=simulation.id)
        self.assertEqual(simulation.batch_job_id, job_id)

    def test_update_status(self):
        simulation = Simulation.objects.create(group=self.group)
        self.assertEqual(simulation.status, sim_status.READY_TO_RUN)

        simulation_url = self.live_server_url + ('/api/v1/simulations/%s/' % simulation.id)
        simulation_db_rec = database_api.get_simulation_record(simulation_url)
        for new_status in (sim_status.STARTED_SCRIPT,
                           sim_status.STAGING_INPUT,
                           sim_status.RUNNING_MODEL,
                           sim_status.STAGING_OUTPUT,
                           sim_status.SCRIPT_DONE):
            simulation_db_rec.update_status(new_status)
            simulation = Simulation.objects.get(id=simulation.id)  # Refetch the model instance from DB
            self.assertEqual(simulation.status, new_status)

    def test_error_occurred(self):
        simulation = Simulation.objects.create(group=self.group)
        self.assertEqual(simulation.status, sim_status.READY_TO_RUN)

        simulation_url = self.live_server_url + ('/api/v1/simulations/%s/' % simulation.id)
        simulation_db_rec = database_api.get_simulation_record(simulation_url)
        error_status = sim_status.SCRIPT_ERROR
        error_details = 'AssertionError: "foo" != "bar"'
        simulation_db_rec.error_occurred(error_status, error_details)

        simulation = Simulation.objects.get(id=simulation.id)  # Refetch the model instance from DB
        self.assertEqual(simulation.status, error_status)
        self.assertEqual(simulation.error_details, error_details)