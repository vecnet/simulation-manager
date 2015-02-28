from .common import *

allowed_hosts = {
    'vecnet02': ['vecnet02.crc.nd.edu'],
    'vecnet1': ['vecnet1.jcu.vecnet.org'],
}
ALLOWED_HOSTS = allowed_hosts[HOSTNAME]

if HOSTNAME == "vecnet1":
    # Override working directories for sim_manager at JCU cluster
    # GROUP_WORKING_DIRS = path('/shared/sim_manager/working-dirs/sim-groups/')
    # SIMULATION_WORKING_DIRS = path('/shared/sim_manager/working-dirs/simulations/')
    pass

# Override settings if necessary
try:
    from .local import *
except ImportError:
    pass