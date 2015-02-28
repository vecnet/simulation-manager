import os.path
from subprocess import PIPE, CalledProcessError

import psutil

from .api import BatchSystemApi


class PortableBatchSystem(BatchSystemApi):
    """
    Implementation of the API using the Portable Batch System (PBS) and its variants (e.g., Torque).
    """

    def submit_job(self, executable, working_dir, *args):
        """
        Implements the BatchSystemApi's submit_job (link to its documentation).
        """
        # Create pbs.sh script in the working directory
        filename = os.path.join(working_dir, "pbs.sh")
        with open(filename, "w") as f:
            arguments = " ".join(args)
            lines = (
                "#!/bin/bash",
                "#PBS -N OpenMalaria",
                '#PBS -d %s' % working_dir,
                '#PBS -l nodes=1:ppn=1',
                '#PBS -V',
                "cd '%s'" % working_dir,
                "%s %s" % (executable, arguments),
            )
            for line in lines:
                f.write(line + '\n')

        # Run qsub command
        # Note - we assume that working directories on headnode and compute node are the same
        cmd = ["qsub"] + [filename]
        try:
            p = psutil.Popen(cmd, cwd=working_dir, stdout=PIPE)
        except CalledProcessError:
            return None
        # Read pid from STDOUT
        (pid, _) = p.communicate()
        pid = pid.strip("\r\n")

        return pid

