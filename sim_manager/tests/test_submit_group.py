# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Tests for the submit_group.py script.
"""

import random
import sys

from crc_nd.utils.test_io import WritesOutputFiles
from django.test import LiveServerTestCase
from mock import patch
from path import path
from vecnet.simulation import ExecutionRequest, sim_model, Simulation, SimulationGroup as SimGroup, submission_status

from .constants import TEST_OUTPUT_ROOT
from .mixins import UsesDatabaseApi
from sim_manager import scripts, working_dirs
from sim_manager.models import SimulationGroup
from sim_manager.scripts import api_urls, batch, input_files, submit_group
from sim_manager.scripts.batch import test_utils
from sim_manager.scripts.constants import SIMULATION_DEFINITION_FILENAME, SIMULATION_SCRIPT


class MainTests(LiveServerTestCase, UsesDatabaseApi, WritesOutputFiles):
    """
    Tests for the script's main function.
    """

    @classmethod
    def setUpClass(cls):
        super(MainTests, cls).setUpClass()
        cls.setup_database_api_user()
        cls.set_output_root(TEST_OUTPUT_ROOT)
        working_dirs.TestingApi.use_testing_root()

        # Add the scripts package's directory to the module search path so the loading of the batch system in the
        # submit_group.py script works.  When the script is executed at the command line, the package directory will
        # automatically be added to the search path.  But here in the test suite, the package is imported, so it's
        # directory is not added automatically.  Therefore, we explicitly add it.
        scripts_dir = path(scripts.__file__).dirname()
        sys.path.append(scripts_dir)

        cls.simulation_script = scripts_dir / SIMULATION_SCRIPT

    @classmethod
    def tearDownClass(cls):
        cls.remove_database_api_user()
        working_dirs.TestingApi.reset_root_to_default()
        sys.path.pop()

    @patch('sim_manager.scripts.submit_group.BATCH_SYSTEM', batch.MOCK)
    def test_run_script(self):
        group = SimulationGroup.objects.create(submitter=self.test_user)
        self.group_id = group.id
        self.assertEqual(group.script_status, submission_status.READY_TO_RUN)

        self.sim_group = SimGroup()
        simulation_1 = Simulation(model=sim_model.OPEN_MALARIA, model_version='32', id_on_client='349',
                                  output_url='http://ingestor.example.com/output-files/')
        simulation_1.input_files['scenario.xml'] = 'http://www.example.com/data/scenarios/1234/scenario.xml'
        simulation_2 = Simulation(model=sim_model.EMOD, model_version='1.6', cmd_line_args=['--foo', 'bar'],
                                  id_on_client='350', output_url=simulation_1.output_url)
        simulation_2.input_files['config.json'] = 'https://files.vecnet.org/4710584372'
        simulation_2.input_files['campaign.json'] = 'https://files.vecnet.org/678109'
        self.sim_group.simulations = [simulation_1, simulation_2]
        self.execution_request = ExecutionRequest(simulation_group=self.sim_group)
        group.setup_working_dir(self.execution_request)

        group_url = self.live_server_url + ('/api/v1/sim-groups/%s/' % group.id)
        simulations_url = self.live_server_url + '/api/v1/simulations/'
        api_urls.write_for_group(group.working_dir, group_url, simulations_url)

        self.check_expected_state = self.expect_script_started
        group.working_dir.chdir()
        self.initialize_output_dir()
        stdout = self.get_output_dir() / 'stdout.txt'
        with stdout.open('w') as f:
            exit_status = submit_group.main('foo', 'bar', stdout=f, test_callback=self.callback)
        self.assertEqual(exit_status, 0)
        group = SimulationGroup.objects.get(id=group.id)
        self.assertEqual(group.script_status, submission_status.SCRIPT_DONE)

    def callback(self):
        if self.check_expected_state:
            self.check_expected_state()
        else:
            self.fail('callback unexpectedly called')

    def expect_script_started(self):
        """
        Confirm that the submission script was started.
        """
        self.assertGroupScriptStatus(submission_status.STARTED_SCRIPT)
        self.check_expected_state = self.expect_cached_files

    def expect_cached_files(self):
        """
        Confirm that the submission script cached input files.
        """
        self.assertGroupScriptStatus(submission_status.CACHING_FILES)
        self.assertTrue(input_files.TestingApi.add_to_cache_mock.called)
        args, kwargs = input_files.TestingApi.add_to_cache_mock.call_args
        self.assertEqual((self.execution_request.input_files,), args)
        self.check_expected_state = self.expect_simulation_created
        self.simulations_created = 0
        test_utils.Mocks.submit_job.reset_mock()
        test_utils.Mocks.submit_job.return_value = generate_job_id()

    def expect_simulation_created(self):
        """
        Confirm that the submission script has created a new simulation in the database.
        """
        self.assertGroupScriptStatus(submission_status.SUBMITTING_JOBS)
        group = SimulationGroup.objects.get(id=self.group_id)
        self.assertEqual(group.simulation_set.count(), self.simulations_created + 1)
        self.simulations_created += 1

        # Check that the working directory is set up properly for the simulation that was just created
        simulation = group.simulation_set.order_by('created_when').last()
        self.assertTrue(simulation.working_dir.isdir())
        sim_definition_path = simulation.working_dir / SIMULATION_DEFINITION_FILENAME
        self.assertTrue(sim_definition_path.isfile())
        sim_definition = Simulation.read_json_file(sim_definition_path)
        expected_sim_definition = self.sim_group.simulations[self.simulations_created - 1]
        self.assertEqual(sim_definition.model, expected_sim_definition.model)
        self.assertEqual(sim_definition.model_version, expected_sim_definition.model_version)
        self.assertEqual(sim_definition.input_files, expected_sim_definition.input_files)
        self.assertEqual(sim_definition.cmd_line_args, expected_sim_definition.cmd_line_args)
        self.assertEqual(sim_definition.id_on_client, expected_sim_definition.id_on_client)
        self.assertEqual(sim_definition.output_url, expected_sim_definition.output_url)

        # Check that the simulation was submitted to the batch system.
        self.assertTrue(test_utils.Mocks.submit_job.called)
        args, kwargs = test_utils.Mocks.submit_job.call_args
        executable, working_dir, cmd_args = args[0], args[1], args[2:]
        self.assertEqual(executable, sys.executable)
        self.assertEqual(working_dir, simulation.working_dir)
        self.assertEqual(list(cmd_args), [self.simulation_script])
        self.assertEqual(simulation.batch_job_id, test_utils.Mocks.submit_job.return_value)
        test_utils.Mocks.submit_job.reset_mock()

        if self.simulations_created < len(self.sim_group.simulations):
            test_utils.Mocks.submit_job.return_value = generate_job_id()
        else:
            self.check_expected_state = None

    def assertGroupScriptStatus(self, expected_status):
        group = SimulationGroup.objects.get(id=self.group_id)
        self.assertEqual(group.script_status, expected_status)


def generate_job_id():
    return str(random.randint(1, 100000))