# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Print the current process id and the script arguments on separate lines in
an output file.  Used for testing.
"""

import os
import sys

with open('stdout.txt', 'w') as out:
    print >>out, os.getpid()
    for arg in sys.argv:
        print >>out, arg
