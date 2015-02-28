import mock

from .api import BatchSystemApi


class Mocks:
    submit_job = mock.MagicMock()


class MockBatchSystem(BatchSystemApi):
    """
    Mock batch system for testing.
    """

    def submit_job(self, executable, working_dir, *args):
        return Mocks.submit_job(executable, working_dir, *args)