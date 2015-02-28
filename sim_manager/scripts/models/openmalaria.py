import os
import shutil
import subprocess

from vecnet.simulation import sim_model

from . import base


OUTPUT_FILENAMES = ('ctsout.txt', 'output.txt')


class SimulationModel(base.SimulationModel):
    """
    OpenMalaria simulation model.
    """

    def __init__(self, version, executable):
        super(SimulationModel, self).__init__(sim_model.OPEN_MALARIA, version, OUTPUT_FILENAMES)
        assert os.path.isfile(executable)
        self.executable = executable
        self.om_install_dir = os.path.dirname(executable)
        self.schema_filename = 'scenario_%s.xsd' % version
        self.schema_path = os.path.join(self.om_install_dir, self.schema_filename)
        assert os.path.isfile(self.schema_path)

    def run(self, scenario):
        """
        Run a model scenario.
        """
        working_dir = os.getcwd()
        shutil.copy(self.schema_path, working_dir)
        scenario_path = os.path.join(working_dir, 'scenario.xml')
        args = [ self.executable,
                 '-p', self.om_install_dir,  # where to find densities.csv
                 '-s', scenario_path,  # if not absolute, will look in -p dir
        ]
        with open('model_stdout_stderr.txt', 'w', buffering=1) as f:
            exit_status = subprocess.call(args,
                                          stdout=f, stderr=subprocess.STDOUT,
                                          cwd=working_dir)
        return exit_status
