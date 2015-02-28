# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json

from crc_nd.utils.test_io import WritesOutputFiles
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from mock import patch
from path import path
from requests import ConnectionError
from requests.exceptions import HTTPError
from vecnet.simulation import Simulation

from .. import views
from ..scripts import run_simulation
from ..scripts.tests.test_utils import add_newlines, LOREM_IPSUM, SAMPLE_CSV_DATA


class OutputStagingTests(LiveServerTestCase, WritesOutputFiles):
    """
    Tests of staging a simulation's output data to its output URL.
    """

    @classmethod
    def setUpClass(cls):
        super(OutputStagingTests, cls).setUpClass()
        output_root = path(__file__).dirname() / 'output'
        cls.set_output_root(output_root)
        cls.test_output_url = reverse('test-output-url')
        cls.simulation = Simulation(id_on_client='007')

    def setUp(self):
        # The output_url is set in this instance method because live_server_url can't be referenced in setUpClass.
        self.simulation.output_url = self.live_server_url + self.test_output_url

    @classmethod
    def tearDownClass(cls):
        views.status_to_return = None
        super(OutputStagingTests, cls).tearDownClass()

    def create_test_file(self, filename, lines):
        file_path = self.get_output_dir() / filename
        file_path.write_lines(lines)

    def test_none(self):
        """
        Test that if the status_to_return is None, then a HttpResponseNotFound is returned.
        """
        views.status_to_return = None
        resp = self.client.post(self.test_output_url)
        self.assertEqual(resp.status_code, 404)

    @patch('sim_manager.scripts.run_simulation.logger')
    def test_post_no_files(self, mock_logger):
        views.status_to_return = 200
        run_simulation.stage_output_files([], simulation=self.simulation)

        self.assertEqual(views.captured_request['method'], 'POST')
        data = json.loads(views.captured_request['body'])
        expected_data = {
            "id_on_client": self.simulation.id_on_client,
            "output_files": {},
        }
        self.assertEqual(data, expected_data)

    @patch('sim_manager.scripts.run_simulation.logger')
    def test_post_2_files(self, mock_logger):
        views.status_to_return = 200

        self.initialize_output_dir()
        self.expected_output_files = dict()
        for filename, file_contents in (
            ('lorem.txt', LOREM_IPSUM),
            ('sample_data.csv', SAMPLE_CSV_DATA),
        ):
            self.create_test_file(filename, file_contents)
            self.expected_output_files[filename] = add_newlines(file_contents)

        self.get_output_dir().chdir()  # Since the output files are read from the current working directory
        run_simulation.stage_output_files(self.expected_output_files.keys(), simulation=self.simulation)

        self.assertEqual(views.captured_request['method'], 'POST')
        data = json.loads(views.captured_request['body'])
        expected_data = {
            "id_on_client": self.simulation.id_on_client,
            "output_files": self.expected_output_files,
        }
        self.assertEqual(data, expected_data)

    @patch('sim_manager.scripts.run_simulation.logger')
    def test_post_fails_401(self, mock_logger):
        """
        Test the stage_output_files function when the POST to the output_url fails with 401 response.
        """
        views.status_to_return = 401
        self.assertRaises(HTTPError, run_simulation.stage_output_files, [], simulation=self.simulation)

    @patch('sim_manager.scripts.run_simulation.logger')
    def test_post_conn_error(self, mock_logger):
        """
        Test the stage_output_files function when the POST to the output_url fails with a connection error.
        """
        self.simulation.output_url='http://HostNotExist.vecnet.org/test-output-url'
        self.assertRaises(ConnectionError, run_simulation.stage_output_files, [], simulation=self.simulation)
