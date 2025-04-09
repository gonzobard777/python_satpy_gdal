from contract import ProjType
from geotif2tile import generate_sat_tile
from constant import C

def wrap(
    filename: str,
    projection: str,
    z: int, x: int, y: int,
)->None:
    generate_sat_tile(
    f'{C.ASSET_DIR}/{filename}.tif',
    f'{C.ASSET_DIR}/result/{projection}_{z}_{x}_{y}_{filename}.png',
    z,x,y,
    projection)


def make_tiles(filenames: list[str], tiles: list[tuple[int,int,int]], proj_type: str)->None:
    for filename in filenames:
        for z,x,y in tiles:
            wrap(filename, proj_type, z, x, y, )


### MSG

filenames_msg = [
'MSG2-VIS006-20250401_0900',
'MSG2-VIS006-20250401_0900_axisswapped',
'MSG3_VIS006-20250401_1200',
]
make_tiles(filenames_msg,[(4,9,7),(4,10,6)], ProjType.Mercator)
make_tiles(filenames_msg,[(4,7,10),(4,8,10),(5,13,17)], ProjType.StereoNorth)


### Himawari

filenames_himawari = [
'Himawari_VIS_20250401_0300',
'Himawari_VIS_20250405_0300',
]
make_tiles(filenames_himawari,[(3,7,4),(6,52,36)], ProjType.Mercator)
make_tiles(filenames_himawari,[(4,9,8),(4,12,11)], ProjType.StereoNorth)


### Тайлики режем из скорректированного GeoTIFF'a (см. adjust_geotiff.py)

filenames_adjust_geotiff = [
'a1_20250401110000_ch04_adjusted-image-1',
]
make_tiles(filenames_adjust_geotiff,[(2,1,1),(2,2,1),(2,2,2),(2,1,2)], ProjType.StereoNorth)


