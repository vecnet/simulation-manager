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
