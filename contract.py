from enum import IntEnum

class ProjType(IntEnum):
    StereoNorth = 1
    Mercator = 3

class SatId(IntEnum):
    MSG2 = 1,
    MSG3 = 2,
    Himawari = 3,
    PlanetA1 = 4,
    PlanetA2 = 5,
    PlanetE2 = 6,
    PlanetE3 = 7,
    PlanetE4 = 8,
