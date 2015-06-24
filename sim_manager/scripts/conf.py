# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

#  Configuration settings for scripts

import socket

import batch
from models import Mock, openmalaria
from sim_manager.scripts.models import emod


hostname = socket.gethostname().split('.')[0]

MODELS = [
    Mock.SimulationModel('0.1'),
]

BATCH_SYSTEM = batch.PSUTIL

if hostname == 'vecnet02':  # Notre Dame Development PBS/Torque Cluster
    MODELS += [
        openmalaria.SimulationModel('30', '/opt/OM/dependencies/openMalaria'),
        openmalaria.SimulationModel('32', '/opt/openmalaria/32/openMalaria'),
        openmalaria.SimulationModel('33', '/opt/openmalaria/33/openMalaria'),
    ]

if hostname in ('vecnet1', 'vecnet2', 'vecnet3', 'vecnet4'):  # JCU cluster
    MODELS += [
        openmalaria.SimulationModel('30', '/shared/sim_manager/openmalaria/30.3/openMalaria'),
        openmalaria.SimulationModel('32', '/shared/sim_manager/openmalaria/32/openMalaria'),
    ]
    BATCH_SYSTEM = batch.PBS

"""
# Example of conf_local.py file
from models import Mock, openmalaria
MODELS = [
   openmalaria.SimulationModel('32', 'D:\\bin\\OM\\32\\openMalaria')
]
"""

try:
    from conf_local import MODELS as LOCAL_MODELS
    MODELS += LOCAL_MODELS
except ImportError:
    LOCAL_MODELS = []  # To satisfy PyCharm code inspector
    pass
