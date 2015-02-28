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
