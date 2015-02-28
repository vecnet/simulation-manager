# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from abc import ABCMeta, abstractmethod


class BatchSystemApi(object):
    """
    API for batch systems.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def submit_job(self, executable, working_dir, *args):
        """
        Submit a job to the batch system's scheduler for execution.

        :param str executable: Path to the program to execute.
        :param str working_dir: Path to the working directory where to execute the program.
        :param args: Command line arguments for the program.

        :return str: The batch job's identifier.
        """
        raise NotImplementedError
