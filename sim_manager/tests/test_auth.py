import mock

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from crc_nd.utils.error_mixins import CallerErrorMixin
from crc_nd.utils.test_io import WritesOutputFiles

from .constants import TEST_OUTPUT_ROOT
from sim_manager import auth
from sim_manager.models import get_api_key


class ScriptUserTests(TestCase, WritesOutputFiles, CallerErrorMixin):
    """
    Tests of the script-user methods in auth module.
    """

    @classmethod
    def setUpClass(cls):
        cls.set_output_root(TEST_OUTPUT_ROOT)

    def tearDown(self):
        #  Ensure we don't leave a path created by a test in place.
        auth.TestingApi.reset_secrets_path()

    def create_script_user(self):
        user = User.objects.create_user(auth.SCRIPT_USER)
        self.assertIsInstance(user, User)
        return user

    def test_unique_names(self):
        """
        Test that the unique constraint on user names is working.
        """
        self.create_script_user()
        self.assertRaises(IntegrityError, User.objects.create_user, auth.SCRIPT_USER)

    def test_not_exist(self):
        """
        Test the script_user_exists function when user does not exist.
        """
        self.assertFalse(User.objects.all().exists())
        self.assertFalse(auth.script_user_exists())

    def test_user_exists(self):
        """
        Test the script_user_exists function when user does exist.
        """
        self.assertFalse(User.objects.all().exists())
        self.create_script_user()
        self.assertTrue(auth.script_user_exists())

    @mock.patch('sim_manager.auth.User.objects.filter')
    def test_multiple_users(self, mock_filter):
        """
        Test the script_user_exists function when multiple script users exist.  This shouldn't happen because of the
        unique constraint on the name column.  But we want to make sure the assert statement in the function works
        correctly.  That's why we need to mock some of the function's internals.
        """
        self.create_script_user()
        user2 = User.objects.create_user(auth.SCRIPT_USER + '2')
        self.assertIsInstance(user2, User)
        mock_filter.return_value = User.objects.all()  # Have it return both users regardless of their names
        self.assertCallerError(auth.Errors.MULTIPLE_USERS_EXIST, auth.script_user_exists)

    def test_create_user(self):
        """
        Test the create_script_user function.
        """
        self.initialize_output_dir()
        secrets_path = self.get_output_dir() / auth.SECRETS_FILE
        auth.TestingApi.set_secrets_path(secrets_path)

        self.assertFalse(User.objects.all().exists())
        auth.create_script_user()
        script_user = User.objects.get(username=auth.SCRIPT_USER)

        # Check the secrets module
        self.assertTrue(auth.get_secrets_path().exists())
        secrets = dict()
        execfile(secrets_path, secrets)
        self.assertEqual(secrets['USERNAME'], auth.SCRIPT_USER)
        self.assertEqual(secrets['API_KEY'], get_api_key(script_user))

    def test_create_user_when_user_exists(self):
        """
        Test the create_script_user function when the script user already exists
        """
        self.assertFalse(User.objects.all().exists())
        self.create_script_user()
        self.assertCallerError(auth.Errors.SCRIPT_USER_EXISTS, auth.create_script_user)

    def test_delete_user(self):
        """
        Test the delete_script_user function
        """
        self.initialize_output_dir()
        secrets_path = self.get_output_dir() / auth.SECRETS_FILE
        auth.TestingApi.set_secrets_path(secrets_path)
        secrets_pyc_path = auth.get_secrets_path().stripext() + '.pyc'

        self.assertFalse(User.objects.all().exists())
        self.create_script_user()
        with open(auth.get_secrets_path(), 'w') as f:
            f.write('Dummy contents for unit test\n')
        secrets_pyc_path.touch()
        auth.delete_script_user()
        self.assertFalse(User.objects.filter(username=auth.SCRIPT_USER).exists())
        self.assertFalse(auth.get_secrets_path().exists())
        self.assertFalse(secrets_pyc_path.exists())

    def test_delete_user_when_no_user(self):
        """
        Test the delete_script_user function when the script user does not exist
        """
        self.assertFalse(User.objects.all().exists())
        try:
            auth.delete_script_user()
        except Exception as exc:
            self.fail('auth.delete_script_user raised exception: %s' % repr(exc))
