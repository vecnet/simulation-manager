# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Tests for the psutil-based implementation of the batch system API.
"""

import os
import sys

from crc_nd.utils.test_io import WritesOutputFiles
from path import path

from .constants import TEST_OUTPUT_ROOT
from ..psutil_impl import SimpleBatchSystem


class SubmitJobTests(WritesOutputFiles):
    """
    Tests of the submit_job method.
    """

    @classmethod
    def setUpClass(cls):
        cls.set_output_root(TEST_OUTPUT_ROOT / 'psutil')

    def test_python_executable(self):
        """
        Test the submit_job method with the Python executable.
        """
        simple_batch_system = SimpleBatchSystem()

        this_dir = path(__file__).abspath().dirname()
        script = this_dir / 'print_pid_and_args.py'
        working_dir = self.get_output_dir()
        self.initialize_output_dir()
        script_args = ('foo', 42, 'hello world')
        job_number = simple_batch_system.submit_job(sys.executable, working_dir, script, *script_args)

        #  The test script writes the following information to a text file:
        #    process id
        #    sys.argv[0]   <-- script path
        #    sys.argv[1]   <-- script_args[0]
        #    sys.argv[2]   <-- script_args[1]
        #    ...
        os.waitpid(job_number, 0)
        stdout = working_dir / 'stdout.txt'
        stdout_lines = stdout.lines()
        pid_in_stdout = int(stdout_lines[0])
        self.assertEqual(job_number, pid_in_stdout)
        args_in_stdout = [x.rstrip('\n') for x in stdout_lines[1:]]
        self.assertEqual(args_in_stdout, [script] + [str(x) for x in script_args])