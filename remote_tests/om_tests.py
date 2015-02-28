# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import unittest
from urlparse import urlparse

import requests
from vecnet.simulation import ExecutionRequest, sim_model, Simulation, SimulationGroup

from conf import Api, Settings


class OpenMalariaTests(unittest.TestCase):
    """
    Tests with OpenMalaria simulations
    """
    def test_1_simulation(self):
        simulation = Simulation(model=sim_model.OPEN_MALARIA, model_version='30', id_on_client='9876')
        scenario_url = 'http://openmalaria.googlecode.com/svn/application_deployment/examples/scenarioVecMonthly.xml'
        simulation.input_files['scenario.xml'] = scenario_url
        sim_group = SimulationGroup(simulations=[simulation])
        execution_request = ExecutionRequest(simulation_group=sim_group)

        groups_endpoint_path = Api.make_full_url_path('sim-groups')
        groups_endpoint_url = Api.make_url(groups_endpoint_path)

        username = Settings.user
        api_key = Settings.api_key
        headers = {
            'Authorization': "ApiKey %s:%s" % (username, api_key),
            'Content-type': "application/json",
        }

        request_data = json.dumps(execution_request.to_dict())
        resp = requests.post(groups_endpoint_url, data=request_data, headers=headers)
        self.assertEqual(resp.status_code, 201)

        # Check that the Location header has the new group's URL
        location = resp.headers['Location']
        self.assertTrue(location.startswith(groups_endpoint_url))
        group_url = urlparse(location)
        path_from_endpoint = group_url.path[len(groups_endpoint_path):]
        self.assertRegexpMatches(path_from_endpoint, r'^\d+/$')  # Check for the new group's id at end of URL
