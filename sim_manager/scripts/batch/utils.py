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
