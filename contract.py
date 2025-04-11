from enum import IntEnum
from enum import StrEnum

class ProjType(StrEnum):
    Mercator = 'mercator'
    StereoNorth = 'stereonorth'

class SatId(IntEnum):
    MSG2 = 1,
    MSG3 = 2,
    Himawari = 3,
    PlanetA1 = 4,
    PlanetA2 = 5,
    PlanetE2 = 6,
    PlanetE3 = 7,
    PlanetE4 = 8,
