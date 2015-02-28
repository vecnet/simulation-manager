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