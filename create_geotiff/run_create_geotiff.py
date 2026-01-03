from constant import C
from create_geotiff import create_geotiff

raster_file_name = 'piter_cell.png'
geotif_file_name = 'geotiff.tif'

create_geotiff(
    f"{C.ASSET_DIR}/result/{geotif_file_name}",
    f"{C.ASSET_DIR}/create_geotiff_raster/{raster_file_name}",
    [-36.58136622494737, 65.66790173424096],
    [147.45001377822678, 71.8535678544176],
    [24.82270010664891, 43.75793517648952],
    "+proj=stere +lat_0=90 +lon_0=65 +R=6371008"
)

# proj_desc = "+proj=stere +lat_0=90 +lon_0=65 +R=6371008"
#
# dd = compute_geotiff_pixelsize(
#     [-70.53687140688633, 72.278359597288462],
#     [117.44133973568756, 65.18052142565738],
#     [0.9247186028159292, 46.96456586739599],
#     proj_desc,
#     800,
#     800,
# )
# print(dd)
#
# dd = compute_geotiff_pixelsize(
#     [-36.58136622494737, 65.66790173424096],
#     [147.45001377822678, 71.8535678544176],
#     [24.82270010664891, 43.75793517648952],
#     proj_desc,
#     800,
#     800,
# )
# print(dd)
