# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
A simple API to records in the Django database for console scripts.
"""

import importlib
import json
import logging

import requests
from vecnet.simulation import sim_status, submission_status


logger = logging.getLogger(__name__)


class Credentials(object):
    """
    Credentials for accessing the database's REST API.
    """

    def __init__(self, username, api_key):
        self.username = username
        self.api_key = api_key

    def for_http_header(self):
        """
        Return the credentials formatted for a HTTP Authorization header
        """
        return "ApiKey %s:%s" % (self.username, self.api_key)

    @staticmethod
    def load_from_secrets_file():
        """
        Load a set of credentials from the secrets module.
        """
        # We use the importlib library since the secrets module is created when a deployment is configured.  This
        # approach keeps PyCharm from complaining.
        secrets = importlib.import_module('secrets')
        return Credentials(secrets.USERNAME, secrets.API_KEY)


class DatabaseRecord(object):
    """
    Base class for the proxy classes for various records in the database.
    """

    def __init__(self, url, credentials):
        self.url = url
        self.credentials = credentials
        self.headers = {
            'Authorization': self.credentials.for_http_header(),
            'Content-type': 'application/json',
        }

    def update_fields(self, **new_field_values):
        """
        Update certain fields of the database record
        """
        body = json.dumps(new_field_values)
        resp = requests.patch(self.url, data=body, headers=self.headers)
        #  Contrary to the Tastypie 0.11.2 documentation, status code 202 (Accepted) is always returned
        if resp.status_code != 202:
            logger.warn('Expected response status 202, but got %d instead' % resp.status_code)


class GroupRecord(DatabaseRecord):
    """
    The proxy for a simulation group's database record.
    """

    def __init__(self, group_url, simulations_url, credentials):
        super(GroupRecord, self).__init__(group_url, credentials)
        self.simulations_url = simulations_url

    def update_script_status(self, status):
        """
        Updates the group's script status in its database record.
        """
        assert submission_status.is_valid(status)
        self.update_fields(script_status=status)

    def add_new_simulation(self, **field_values):
        """
        Create a new simulation in the database and relate it to this group.

        :param data_fields: the values to assign to certain fields in the new database record
        :return: A 2-tuple: (the proxy for the simulation's database record, path to simulation's working directory)
        """
        field_values["group"] = self.url
        body = json.dumps(field_values)
        resp = requests.post(self.simulations_url, data=body, headers=self.headers)
        if resp.status_code == 201:
            simulation_url = resp.headers['Location']
            resp_data = json.loads(resp.content)
            working_dir = resp_data['working_dir']
            return SimulationRecord(simulation_url, self.credentials), working_dir
        else:
            raise RuntimeError('Expected response status 201, but got %d instead' % resp.status_code)


class SimulationRecord(DatabaseRecord):
    """
    The proxy for a simulation's database record.
    """

    def __init__(self, url, credentials):
        super(SimulationRecord, self).__init__(url, credentials)

    def set_batch_job(self, job_id):
        """
        Set the batch_job_id field in the simulation's database record.
        """
        assert isinstance(job_id, basestring)
        self.update_fields(batch_job_id=job_id)

    def update_status(self, new_status):
        """
        Update the status field in the simulation's database record.
        """
        assert sim_status.is_valid(new_status)
        self.update_fields(status=new_status)

    def error_occurred(self, error_status, error_details):
        """
        Update the sim_status and error_details fields in the simulation's database record to indicate that an
        error occurred.
        """
        assert sim_status.is_valid(error_status)
        assert isinstance(error_details, basestring)
        self.update_fields(status=error_status, error_details=error_details)


_credentials = None


def _get_credentials():
    global _credentials
    if _credentials is None:
        _credentials = Credentials.load_from_secrets_file()
    return _credentials


def get_group_record(group_url, simulation_url):
    """
    Get the proxy for a simulation group's database record.
    """
    return GroupRecord(group_url, simulation_url, _get_credentials())


def get_simulation_record(simulation_url):
    """
    Get the proxy for a simulation's database record.
    """
    return SimulationRecord(simulation_url, _get_credentials())


class TestingApi:
    """
    API for unit tests.
    """

    @staticmethod
    def set_credentials(username, api_key):
        global _credentials
        _credentials = Credentials(username, api_key)

    @staticmethod
    def clear_credentials():
        """
        Clear any stored credentials.  If they are not explictly set before the next time they are used within the
        module, they will be loaded from the secrets module.
        """
        global _credentials
        _credentials = None
