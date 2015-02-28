"""
Submit the simulations in a group to the batch system.
"""

import os
import path
import sys

import api_urls
from batch.utils import load_batch_system
from conf import BATCH_SYSTEM
from constants import EXECUTION_REQUEST_FILENAME, SIMULATION_DEFINITION_FILENAME, SIMULATION_SCRIPT
import database_api
import input_files

from vecnet.simulation import ExecutionRequest
from vecnet.simulation.submission_status import (
    STARTED_SCRIPT,
    CACHING_FILES,
    SUBMITTING_JOBS,
    SCRIPT_DONE,
    SCRIPT_ERROR,
)


def main(*args, **kwargs):
    """
    The main algorithm of the script.

    :param args: Sequence of command-line arguments
    :param kwargs: Special parameters for testing purposes.  They are provided when the script is imported as a module.
    :return: exit status
    """
    # If stdout is specified, it's used as the target of the script's "print" statements.  If it's not specified,
    # then sys.stdout is used by default.
    stdout = kwargs.get('stdout')
    if stdout is None:
        stdout = sys.stdout

    # If test_callback is specified, it's called at certain milestones in the script to allow test code to check
    # the current state of the system (e.g., database contents, data on filesystem, etc).
    test_callback = kwargs.get('test_callback')
    if test_callback is not None:
        assert callable(test_callback)

    # Print basic information about the running process
    print >>stdout, 'process id =', os.getpid()
    working_dir = path.path.getcwd()
    print >>stdout, 'working directory =', working_dir
    print >>stdout, 'args = [', ', '.join('"%s"' % x for x in args), ']'

    print >>stdout, 'Loading API URLs ...'
    group_url, simulations_url = api_urls.read_for_group(working_dir)
    print >>stdout, '  group_url =', group_url
    print >>stdout, '  simulations_url =', simulations_url

    group_db_rec = database_api.get_group_record(group_url, simulations_url)
    group_db_rec.update_script_status(STARTED_SCRIPT)
    if test_callback:
        test_callback()

    print >>stdout, "Loading execution request ..."
    execution_request_path = working_dir / EXECUTION_REQUEST_FILENAME
    execution_request = ExecutionRequest.read_json_file(execution_request_path)

    group_db_rec.update_script_status(CACHING_FILES)
    input_files.add_to_cache(execution_request.input_files)
    if test_callback:
        test_callback()

    print >>stdout, "Submitting simulations ..."
    group_db_rec.update_script_status(SUBMITTING_JOBS)

    simulation_script = path.path(__file__).dirname() / SIMULATION_SCRIPT
    batch_system = load_batch_system(BATCH_SYSTEM)

    for simulation in execution_request.simulation_group.simulations:
        simulation_db_rec, sim_working_dir = group_db_rec.add_new_simulation(id_on_client=simulation.id_on_client)
        print >>stdout, ' ', simulation_db_rec.url

        # Write the simulation object as JSON to the working directory
        sim_working_dir = path.path(sim_working_dir)
        sim_definition_path = sim_working_dir / SIMULATION_DEFINITION_FILENAME
        simulation.write_json_file(sim_definition_path)

        # Schedule the simulation with the batch system.
        cmd_args = [simulation_script]
        job_id = batch_system.submit_job(sys.executable, sim_working_dir, *cmd_args)
        print >>stdout, '    batch job =', job_id
        if job_id is not None:
            simulation_db_rec.set_batch_job(job_id)
        else:
            # Job submission failed, set this simulation status to SCRIPT_ERROR
            simulation_db_rec.update_status(SCRIPT_ERROR)
            pass

        if test_callback:
            test_callback()

    print >>stdout, "Done"
    group_db_rec.update_script_status(SCRIPT_DONE)

    return 0


if __name__ == '__main__':
    exit_status = main(*sys.argv)
    sys.exit(exit_status)