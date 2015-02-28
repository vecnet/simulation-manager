# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

import psutil

from .api import BatchSystemApi


class SimpleBatchSystem(BatchSystemApi):
    """
    A simple implementation of the API using the psutil library.
    """

    def submit_job(self, executable, working_dir, *args):
        """
        Implements the BatchSystemApi's submit_job (link to its documentation).
        """
        cmd = [executable] + [str(x) for x in args]
        p = psutil.Popen(cmd, cwd=working_dir)
        return str(p.pid)

    def get_status(self, process_id):
        """
        Gets the status of the given simulation using the psutil package and returns it.

        :param int process_id: An integer greater than negative one representing the id of the process to get the
                               status for.
        """
        assert isinstance(process_id, int)
        process = psutil.Process(process_id)
        return process.status()
