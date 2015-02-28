# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.


class Default:
    """
    Default settings
    """
    SERVER = '127.0.0.1:8000'
    USER = 'test-user'


class Settings:
    """
    Actual settings.  These can be changed by command-line arguments (see __main__.py).
    """
    server = Default.SERVER
    user = Default.USER

    api_key = None
    module = []     # List of modules in this package whose tests should be run


class Api:
    """
    Constants and helper functions for the API.
    """

    MAIN_ENDPOINT = '/api/v1/'

    @staticmethod
    def make_full_url_path(*args):
        """
        Makes a full URL path to a resource.

        :param args: The path components from the API's main endpoint to the desired resource.
        :return string: Full URL path
        """
        path = '/'.join(str(x) for x in args)
        if len(path) > 0:
            path += '/'
        return Api.MAIN_ENDPOINT + path

    @staticmethod
    def make_url(resource_path):
        """
        Makes a complete URL to an API resource.

        :param resource_path: The full path on the server to the resource.
        :return: A complete URL
        """
        return 'http://' + Settings.server + resource_path