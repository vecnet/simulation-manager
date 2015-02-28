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
