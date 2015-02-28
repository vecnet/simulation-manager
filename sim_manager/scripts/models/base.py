class SimulationModel(object):
    """
    Base class for simulation models.  An instance represents a particular version of a simulation model available
    on the compute engine.
    """

    def __init__(self, id_, version, output_filenames=None):
        """
        :param string id_: The model's identifier (see vecnet's simulation_models.model_id module)
        :param string version: The identifier for the model version, e.g., '30', '1.2a4', '4.10 (build 7)'.
        :param sequence output_filenames: Names of the model's output files.
        """
        self.id = id_
        self.version = version
        if output_filenames is None:
            output_filenames = list()
        self.output_filenames = output_filenames