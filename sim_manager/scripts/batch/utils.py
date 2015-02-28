# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from . import _ids as ids
from .psutil_impl import SimpleBatchSystem
from .test_utils import MockBatchSystem
from .pbs import PortableBatchSystem

_classes = {
    ids.MOCK: MockBatchSystem,
    ids.PSUTIL: SimpleBatchSystem,
    ids.PBS: PortableBatchSystem
}


def load_batch_system(system_id):
    try:
        batch_system_class = _classes[system_id]
        return batch_system_class()
    except KeyError:
        raise ValueError('Invalid batch system id: "%s"' % system_id)
