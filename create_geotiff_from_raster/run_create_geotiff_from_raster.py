from constant import C
from create_geotiff_from_raster import create_geotiff_from_raster

raster_file_name = 'countries_800x800.png'
geotif_file_name = 'geotiff.tif'

create_geotiff_from_raster(
    "+proj=stere +lat_0=90 +lon_0=65 +R=6371008",
    f"{C.ASSET_DIR}/result/{geotif_file_name}",
    f"{C.ASSET_DIR}/create_geotiff_from_raster/{raster_file_name}",
    [-36.58136622494737, 65.66790173424096],
    [147.45001377822678, 71.8535678544176],
    [24.82270010664891, 43.75793517648952],
)
