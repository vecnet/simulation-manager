# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Input files for simulations.
"""

import mock


def add_to_cache(files):
    """
    Add input files to the local file cache.
    """
    # For now, this function is stubbed out by calling its associated mock object.
    TestingApi.add_to_cache_mock(files)


class TestingApi:
    """
    API for unit tests.
    """
    add_to_cache_mock = mock.MagicMock()
