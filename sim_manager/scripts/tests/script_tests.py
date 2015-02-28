# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import os
import shutil
import subprocess
import sys
import time
import unittest

from .. import constants


class ScriptTestCase(unittest.TestCase):
    """
    Tests for command-line scripts
    """
    @classmethod
    def setUpClass(cls):
        cls.tests_dir = os.path.abspath(os.path.dirname(__file__))
        cls.scripts_dir = os.path.dirname(cls.tests_dir)
        cls.run_simulation_script = os.path.join(cls.scripts_dir, 'run_simulation.py')
        cls.output_dir = os.path.join(cls.tests_dir, 'output')

    def get_working_dir(self, test_name):
        """
        Get the path of the working directory for the test method whose name is provided.
        """
        test_case, test_method = test_name.split('.')[-2:]
        test_case_dir = os.path.join(self.output_dir, test_case)
        working_dir = os.path.join(test_case_dir, test_method)
        return working_dir

    def setup_working_dir(self, working_dir):
        """
        Setup a working directory for a test.  If the directory does not exist, then create it.  If the directory does
        exist, then remove all its contents.
        """
        if os.path.exists(working_dir):
            if os.path.isfile(working_dir):
                self.fail('"%s" is not a directory' % working_dir)
            else:
                # Clear out the directory
                for entry in os.listdir(working_dir):
                    entry_path = os.path.join(working_dir, entry)
                    if os.path.isdir(entry_path):
                        shutil.rmtree(entry_path)
                    else:
                        os.remove(entry_path)
        else:
            os.makedirs(working_dir)

    def run_python_script(self, script, working_dir, max_time=5, poll_interval=0.5):
        """
        Run a Python script in a working directory.  Wait for a given number of seconds for the script to end;
        otherwise, kill it.  If script ends in the given time period, then its exit code is returned.  If the
        script is killed, then None is returned.
        """
        # start the subprocess
        args = [ sys.executable, script ]
        stdout_path = os.path.join(working_dir, 'STDOUT_STDERR')
        with open(stdout_path, 'w') as stdout_file:
            p = subprocess.Popen(args, stdout=stdout_file, stderr=subprocess.STDOUT, cwd=working_dir)
            intervals = int(max_time / poll_interval)
            for interval in range(0, intervals):
                time.sleep(poll_interval)
                if p.poll() is not None:
                    return p.returncode
            if p.poll() is None:
                p.kill()
                return None
            else:
                return p.returncode


class RunMockSimulations(ScriptTestCase):
    """
    Tests that run mock simulations.
    """

    def setup_execution_dir(self, simulation_defn):
        """
        Setup the working directory for a simulation, by ensuring there are no files in it except the JSON
        file with the simulation definition itself.
        """
        self.working_dir = self.get_working_dir(self.id())
        self.setup_working_dir(self.working_dir)

        # dump dict literal as json to working_dir / scripts.constants.SIMULATION_DEFINITION_FILENAME
        sim_defn_path = os.path.join(self.working_dir, constants.SIMULATION_DEFINITION_FILENAME)
        with open(sim_defn_path, 'w') as f:
            json.dump(simulation_defn, f, indent=4)

    def test_with_no_input_files(self):
        """
        Test the run_simulation script with a Mock simulation and version 0.1
        """
        simulation_defn = {
                "model": "Mock",
                "input_files":
                {
                },
            "model_version": "0.1"
        }
        self.setup_execution_dir(simulation_defn)
        return_code = self.run_python_script(self.run_simulation_script, self.working_dir)
        self.assertEqual(return_code, 0)

    def test_with_1_input_file(self):
        """
        Test the execute_scenario script with one input file.
        """
        simulation_defn = {
                "model": "Mock",
                "input_files":
                {
                    "scenario.xml": "http://openmalaria.googlecode.com/svn/application_deployment/examples/scenarioNoInterv.xml",
                },
            "model_version": "0.1"
        }
        self.setup_execution_dir(simulation_defn)
        return_code = self.run_python_script(self.run_simulation_script, self.working_dir)
        self.assertEqual(return_code, 0)
