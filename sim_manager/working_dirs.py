"""
Working directories for simulation groups and individual simulations.
"""

import logging

from crc_nd.utils.file_io import clean_out_dir
from django.conf import settings

from .scripts.constants import EXECUTION_REQUEST_FILENAME
from .tests.constants import TEST_OUTPUT_ROOT

logger = logging.getLogger(__name__)

# The active root directory for group working directories
_group_working_dirs = settings.GROUP_WORKING_DIRS

# The active root directory for simulation working directories
_simulation_working_dirs = settings.SIMULATION_WORKING_DIRS


def get_dir_for_group(group_id):
    """
    Get the path to the group's working directory.

    :param group_id: The group's id.
    :return string: The absolute path to the working directory.
    """
    return _group_working_dirs / str(group_id)


def setup_for_group(group_id, execution_request):
    """
    Set up a working directory for a simulation group.

    :param int group_id: The group's id (used to make a unique path for the working directory).
    :param execution_request: The request to execute the simulation group.
    """
    working_dir = get_dir_for_group(group_id)
    _create_working_dir(working_dir)

    execution_request_file = working_dir / EXECUTION_REQUEST_FILENAME
    execution_request.write_json_file(execution_request_file)


def _create_working_dir(working_dir):
    if working_dir.exists():
        if TestingApi.is_active:
            clean_out_dir(working_dir)
        else:
            logger.warn('Working directory already exists: %s' % working_dir)
    else:
        working_dir.makedirs()
        logging.debug('Created working directory: %s' % working_dir)


def get_dir_for_simulation(simulation_id):
    """
    Get the path to the simulation's working directory.

    :param simulation_id: The simulation's id.
    :return string: The absolute path to the working directory.
    """
    return _simulation_working_dirs / str(simulation_id)


def setup_for_simulation(simulation_id):
    """
    Set up a working directory for a simulation.

    :param int simulation_id: The simulation's id (used to make a unique path for the working directory).
    """
    working_dir = get_dir_for_simulation(simulation_id)
    _create_working_dir(working_dir)


class TestingApi:
    """
    API for testing purposes.
    """
    GROUP_WORKING_DIRS = TEST_OUTPUT_ROOT / 'sim-groups'
    SIMULATION_WORKING_DIRS = TEST_OUTPUT_ROOT / 'simulations'
    is_active = False

    @classmethod
    def use_testing_root(cls):
        """
        Use the testing root directories for the working directories for simulations and their groups.
        """
        global _group_working_dirs, _simulation_working_dirs
        _group_working_dirs = TestingApi.GROUP_WORKING_DIRS
        _simulation_working_dirs = TestingApi.SIMULATION_WORKING_DIRS
        TestingApi.is_active = True

        # #  Remove any existing working dirs.
        # for root in (_group_working_dirs, _simulation_working_dirs):
        #     if root.exists():
        #         for dir in root.dirs():
        #             dir.rmtree()

    @classmethod
    def reset_root_to_default(cls):
        """
        Reset the root directories for the working directories for simulations and their groups back to the defaults
        (SIMULATION_WORKING_DIRS and GROUP_WORKING_DIRS settings).
        """
        global _group_working_dirs, _simulation_working_dirs
        _group_working_dirs = settings.GROUP_WORKING_DIRS
        _simulation_working_dirs = settings.SIMULATION_WORKING_DIRS
        TestingApi.is_active = False
