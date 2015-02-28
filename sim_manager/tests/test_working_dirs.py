# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

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