"""
Asynchronous tasks for submitting a group's simulations to the batch system.
"""

import subprocess

import mock


def start_task(python_executable, python_script, working_dir):
    """
    Start a background task (process) that runs a Python script.

    :param str python_executable: Path to the Python interpreter
    :param str python_script: Path to the Python script to execute
    :param str working_dir: Path to the directory where the script should be executed
    :return: The id of the background task.
    """
    if TestingApi._mock_start_task is not None:
        return TestingApi._mock_start_task(python_script, working_dir)

    args = [python_executable, python_script]  # Defined
    stdout_file = working_dir / 'stdout.txt'
    try:
        process = subprocess.Popen(args, stdout=stdout_file.open('w'), stderr=subprocess.STDOUT, cwd=working_dir)
        return process.pid
    except Exception as exc:
        raise StartError(str(exc))


class StartError(Exception):
    """
    An error occurred when starting a task.
    """
    pass


class TestingApi:
    """
    API for unit tests.
    """

    _mock_start_task = None

    @classmethod
    def disable_start_task(cls):
        """
        Disable the start_task function so it doesn't create another process.  Instead it will return the MagicMock
        object that's returned by this function.
        """
        cls._mock_start_task = mock.MagicMock()
        return cls._mock_start_task

    @classmethod
    def enable_start_task(cls):
        """
        Enable the start_task function to actually create another process.  The function is no longer mocked.
        """
        cls._mock_start_task = None