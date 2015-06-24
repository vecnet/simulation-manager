# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import shutil
import subprocess

from vecnet.simulation import sim_model

from . import base


OUTPUT_FILENAMES = ('BinnedReport.json', 'DemographicsSummary.json', 'InsetChart.json', 'VectorSpeciesReport.json')


class SimulationModel(base.SimulationModel):
    """
    Emod simulation model.
    """

    def __init__(self, version, executable):
        super(SimulationModel, self).__init__(sim_model.EMOD, version, OUTPUT_FILENAMES)
        assert os.path.isfile(executable)
        self.executable = executable

    def run(self, scenario):
        """
        Run a model scenario. eradication.exe -C config.json -I input -O output
        """
        working_dir = os.getcwd()
        args = [
            self.executable,
            '-C', 'config.json',  # where to find densities.csv
            '-I', working_dir,  # if not absolute, will look in -p dir
            '-O', working_dir,
        ]
        with open('model_stdout_stderr.txt', 'w', buffering=1) as f:
            exit_status = subprocess.call(args,
                                          stdout=f, stderr=subprocess.STDOUT,
                                          cwd=working_dir)
        return exit_status
