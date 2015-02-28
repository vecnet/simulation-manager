#  Configuration settings for scripts

import socket

import batch
from models import Mock, openmalaria


hostname = socket.gethostname().split('.')[0]

MODELS = [
    Mock.SimulationModel('0.1'),
]

BATCH_SYSTEM = batch.PSUTIL

if hostname == 'vecnet02': # Notre Dame Development PBS/Torque Cluster
    MODELS += [
        openmalaria.SimulationModel('30', '/opt/OM/dependencies/openMalaria'),
        openmalaria.SimulationModel('32', '/opt/openmalaria/32/openMalaria'),
        openmalaria.SimulationModel('33', '/opt/openmalaria/33/openMalaria'),
    ]

if hostname in ('vecnet1', 'vecnet2', 'vecnet3', 'vecnet4'): # JCU cluster
    MODELS += [
        openmalaria.SimulationModel('30', '/shared/sim_manager/openmalaria/30.3/openMalaria'),
        openmalaria.SimulationModel('32', '/shared/sim_manager/openmalaria/32/openMalaria'),
    ]
    BATCH_SYSTEM = batch.PBS
