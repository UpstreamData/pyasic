from pyasic.miners.backends.elphapex import ElphapexMiner
from pyasic.miners.device.models import DG1, DG1Home, DG1Plus


class ElphapexDG1Plus(ElphapexMiner, DG1Plus):
    pass


class ElphapexDG1(ElphapexMiner, DG1):
    pass


class ElphapexDG1Home(ElphapexMiner, DG1Home):
    pass
