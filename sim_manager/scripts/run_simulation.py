# Execute a model scenario

import json
import logging
import sys
from urlparse import urlparse

from path import path
import requests
from requests.exceptions import HTTPError
from vecnet.simulation import sim_status, Simulation

import api_urls
import conf
import constants
import database_api
from utils import download_file, get_file_contents

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main():
    logger.info('Script started')

    simulation_db_rec = get_database_record()
    simulation_db_rec.update_status(sim_status.STARTED_SCRIPT)

    simulation = Simulation.read_json_file(constants.SIMULATION_DEFINITION_FILENAME)

    sim_model = None
    for model in conf.MODELS:
        if model.id == simulation.model and model.version == simulation.model_version:
            sim_model = model
            break
    assert sim_model is not None, 'Unknown model: {} {}'.format(simulation.model, simulation.model_version)

    simulation_db_rec.update_status(sim_status.STAGING_INPUT)
    get_input_files(simulation.input_files)

    logger.info('Running %s model (version %s)...', sim_model.id, sim_model.version)
    simulation_db_rec.update_status(sim_status.RUNNING_MODEL)
    sim_model.run(simulation)

    simulation_db_rec.update_status(sim_status.STAGING_OUTPUT)
    stage_output_files(sim_model.output_filenames, simulation)

    simulation_db_rec.update_status(sim_status.SCRIPT_DONE)
    logger.info('Script done')


def get_database_record():
    """
    Get the proxy for the simulation's database record.
    """
    working_dir = path.getcwd().abspath()
    simulation_url = api_urls.read_for_simulation(working_dir)
    simulation_db_rec = database_api.get_simulation_record(simulation_url)
    return simulation_db_rec


def get_input_files(files):
    """
    Get the scenario's input files and put them in the working directory.

    :param dict files: Key = local file name to store input file as, value = URL of input file
    """
    for local_name, file_url in files.iteritems():
        scheme = urlparse(file_url).scheme
        if scheme in ('http', 'https'):
            logger.info('Downloading %s from %s ...', local_name, file_url)
            download_file(file_url, local_name)
        else:
            raise NotImplementedError('URL scheme "%s" not supported' % scheme)


def stage_output_files(output_filenames, simulation):
    """
    Stage the simulation's output files by transmitting them to the specified URL.

    :param list output_filenames: Names of the model's output files.
    :param simulation: The simulation definition
    """
    output_url = simulation.output_url
    if output_url is None:
        logger.info('No output files were staged because output_url is None')
        return
    logger.info('Staging output files to %s ...', output_url)

    # Collect the contents of the output files into a dictionary: key = filename, value = list of strings (one per
    # line)
    print_filename_in_log = lambda filename: logger.info('  %s', filename)
    output_files = get_file_contents(output_filenames, print_filename_in_log)

    output_data = dict(id_on_client=simulation.id_on_client, output_files=output_files)
    post_body = json.dumps(output_data)
    resp = requests.post(output_url, data=post_body)
    resp.raise_for_status()  # Raises a requests.exceptions.HTTPError if one occurred


if __name__ == "__main__":
    try:
        logging.basicConfig(filename='run_simulation.log', format='%(asctime)s - %(message)s')
        main()
        sys.exit(0)
    except Exception as exc:
        logger.exception(exc)
        if isinstance(exc, HTTPError):
            error_status = sim_status.OUTPUT_ERROR
        else:
            error_status = sim_status.SCRIPT_ERROR

        # Create a sentinel file to indicate that we're going to attempt to update the database record.  If an
        # exception occurs during the update, then the file will be left intact.  A background task (e.g., cron job)
        # can check for this file, and update the DB record accordingly.
        sentinel_file = path.getcwd().abspath() / constants.SIMULATION_SCRIPT_ERROR_FILE
        sentinel_file.touch()
        simulation_db_rec = get_database_record()
        simulation_db_rec.error_occurred(error_status, repr(exc))
        sentinel_file.unlink()

        sys.exit(1)
