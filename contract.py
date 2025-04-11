from enum import IntEnum
from enum import StrEnum

class ProjType(StrEnum):
    Mercator = 'mercator'
    StereoNorth = 'stereonorth'

class SatId(IntEnum):
    MSG2 = 1,
    MSG3 = 2,
    Himawari = 3,