import unittest

from django.conf import settings

from sim_manager import working_dirs


class GroupDirTests(unittest.TestCase):
    """
    Tests for the methods in the working_dirs module that deal with simulation groups.
    """

    def test_get_dir(self):
        """
        Test the get_dir_for_group method.
        """
        group_working_dirs = str(settings.GROUP_WORKING_DIRS)

        group_5_dir = working_dirs.get_dir_for_group(5)
        self.assertTrue(group_5_dir.startswith(group_working_dirs))

        group_42_dir = working_dirs.get_dir_for_group(42)
        self.assertTrue(group_42_dir.startswith(group_working_dirs))
        self.assertNotEqual(group_42_dir, group_5_dir)