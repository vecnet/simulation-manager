from crc_nd.utils.django import make_choices_tuple
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from tastypie.models import ApiKey, create_api_key
from vecnet.simulation import sim_status, submission_status

from sim_manager import async, working_dirs


#  Hook in the Tastypie function to automatically create an API key for a new User
models.signals.post_save.connect(create_api_key, sender=User)


def get_api_key(user):
    """
    Get the API key for a user.

    :return str: The user's API key
    """
    assert isinstance(user, User)
    return ApiKey.objects.get(user_id=user.id).key


class SimulationGroup(models.Model):
    """
    A group of 1 or more simulations that were submitted together.
    """
    submitter = models.ForeignKey(User)
    submitted_when = models.DateTimeField(auto_now_add=True)
    process_id = models.IntegerField(help_text='id of background process running the group script', null=True)
    script_status = models.CharField(choices=make_choices_tuple(submission_status.ALL,
                                                                submission_status.get_description),
                                     default=submission_status.READY_TO_RUN,
                                     max_length=submission_status.MAX_LENGTH)
    script_error = models.CharField(max_length=255, blank=True)

    def setup_working_dir(self, execution_request):
        """
        Setup the working directory for the simulation group.
        """
        working_dirs.setup_for_group(self.id, execution_request)

    @property
    def working_dir(self):
        """
        The path to the group's working directory.
        """
        return working_dirs.get_dir_for_group(self.id)

    def start_submission_script(self):
        """
        Start the Python script that will submit the group's simulations to the cluster's batch system.
        """
        try:
            python_executable = settings.PYTHON_FOR_SCRIPTS
            self.process_id = async.start_task(python_executable, SimulationGroup.submission_script_path(),
                                               self.working_dir)
            self.save()
            return True
        except async.StartError as exc:
            self.script_error = str(exc)
            self.save()
            return False

    @staticmethod
    def submission_script_path():
        """
        The path to the Python script that submits a group's simulations.
        """
        return settings.PROJECT_ROOT / 'sim_manager' / 'scripts' / 'submit_group.py'


class Simulation(models.Model):
    """
    A single execution of a simulation model.
    """
    created_when = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(SimulationGroup)
    status = models.CharField(choices=make_choices_tuple(sim_status.ALL, sim_status.get_description),
                              default=sim_status.READY_TO_RUN,
                              max_length=sim_status.MAX_LENGTH)
    # Job ID is updated by submit_group.py script using REST API
    batch_job_id = models.CharField(default='', max_length=50,
                                    help_text="Identifier for the simulation's batch job")  # May be integer or string
    id_on_client = models.CharField(default='', max_length=100)
    error_details = models.CharField(default='', max_length=500)

    def setup_working_dir(self):
        """
        Setup the working directory for the simulation.
        """
        working_dirs.setup_for_simulation(self.id)

    @property
    def working_dir(self):
        """
        The path to the simulation's working directory.
        """
        return working_dirs.get_dir_for_simulation(self.id)
