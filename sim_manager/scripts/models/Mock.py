# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from vecnet.simulation import sim_model

from . import base


class SimulationModel(base.SimulationModel):
    """
    Mock simulation model for testing.
    """

    def __init__(self, version):
        super(SimulationModel, self).__init__(sim_model.MOCK, version)

    def run(self, scenario):
        """
        Run a model scenario.
        """
        pass