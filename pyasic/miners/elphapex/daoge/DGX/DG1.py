from pyasic.miners.backends.elphapex import ElphapexMiner
from pyasic.miners.device.models import DG1, DG1Plus


class ElphapexDG1Plus(ElphapexMiner, DG1Plus):
    pass


class ElphapexDG1(ElphapexMiner, DG1):
    pass
