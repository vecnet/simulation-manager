# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Methods for writing and reading API URLs used by the command-line scripts.
"""

import json

API_URLS_FILENAME = 'api_urls.json'


class Keys:
    GROUP_URL = 'group_url'
    SIMULATIONS_URL = 'simulations_url'
    SIMULATION_URL = 'simulation_url'


def write_for_group(working_dir, group_url, simulations_url):
    """
    Write the API URLs that the group's submission script will need.

    :param working_dir: The group's working directory.
    :param group_url: The API URL for the group.
    :param simulations_url: The API endpoint for simulations (list endpoint).
    """
    url_dict = {
        Keys.GROUP_URL: group_url,
        Keys.SIMULATIONS_URL: simulations_url,
    }
    file_path = working_dir / API_URLS_FILENAME
    with file_path.open('w') as f:
        json.dump(url_dict, f, indent=2)


def read_for_group(working_dir):
    """
    Read the API URLs that the group's submission script will need.

    :param working_dir: The group's working directory.

    :return tuple: (group_url, simulations_url)
    """
    file_path = working_dir / API_URLS_FILENAME
    with file_path.open('r') as f:
        url_dict = json.load(f)
    group_url = url_dict[Keys.GROUP_URL]
    simulations_url = url_dict[Keys.SIMULATIONS_URL]
    return (group_url, simulations_url)


def write_for_simulation(working_dir, simulation_url):
    """
    Write the API URLs that the simulation's script will need.

    :param working_dir: The simulation's working directory.
    :param simulation_url: The API URL for the simulation.
    """
    url_dict = {
        Keys.SIMULATION_URL: simulation_url,
    }
    file_path = working_dir / API_URLS_FILENAME
    with file_path.open('w') as f:
        json.dump(url_dict, f, indent=2)


def read_for_simulation(working_dir):
    """
    Read the API URLs that the simulation's script will need.

    :param working_dir: The group's working directory.

    :return str: simulation_url
    """
    file_path = working_dir / API_URLS_FILENAME
    with file_path.open('r') as f:
        url_dict = json.load(f)
    simulation_url = url_dict[Keys.SIMULATION_URL]
    return simulation_url
