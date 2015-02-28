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
