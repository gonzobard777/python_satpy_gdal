import os
import sys
import time
import logging
logging.basicConfig(level=logging.INFO)
import warnings
warnings.filterwarnings("ignore")
import traceback
import subprocess
import argparse
from osgeo import gdal, osr


def generate_sat_tile(
    input_filename: str,
    output_path: str,
    z: int, x: int, y: int,
    projection: str,
    tile_size_x=512, tile_size_y=512,
    output_type="PNG",
    resampling="near"
) -> str | None:

    start_time = time.time()

    inproj = osr.SpatialReference()
    inproj.ImportFromEPSG(4326)

    src_proj = osr.SpatialReference()

    if projection == "mercator":
        left_top_geo = (-179.999999999999, -85.05112877980659)
        right_bottom_geo = (179.999999999999, 85.0511287798066)

        srs = "EPSG:3857"

        src_proj.ImportFromEPSG(3857)
        transform = osr.CoordinateTransformation(inproj, src_proj)

        # projwin_srs = "EPSG:3857"

        proj_min_x, proj_min_y, _ = transform.TransformPoint(*left_top_geo[::-1])
        proj_max_x, proj_max_y, _ = transform.TransformPoint(*right_bottom_geo[::-1])
    elif projection == "stereonorth":
        left_top_geo = (-70, -57.5)
        right_bottom_geo = (110, -57.49999999999997)

        srs = "+proj=stere +lat_0=90 +lon_0=65 +R=6371008"

        # projwin_srs = "+proj=stere +lat_0=90 +lon_0=65"
        src_proj.ImportFromProj4(srs)
        transform = osr.CoordinateTransformation(inproj, src_proj)

        proj_min_x, proj_max_y, _ = transform.TransformPoint(*left_top_geo[::-1])
        proj_max_x, proj_min_y, _ = transform.TransformPoint(*right_bottom_geo[::-1])

        # kek_90_x, kek_90_y, _ = transform.TransformPoint(90, 0)
        # logging.info(f"-> 0 0 point: {kek_90_x}, {kek_90_y}")
    else:
        logging.error(f"Not available projection: {projection}")
        sys.exit(1)
        return None

    # logging.info(f"-> proj min: {proj_min_x}, {proj_min_y}")
    # logging.info(f"-> proj max: {proj_max_x}, {proj_max_y}")

    tile_count = 1 << z

    tile_width = (proj_max_x - proj_min_x) / tile_count
    tile_height = (proj_max_y - proj_min_y) / tile_count

    xoff = proj_min_x + x * tile_width
    yoff = proj_min_y + (tile_count - y - 1) * tile_height  # Потому что geotiff инвертирован по Y

    #output_file_name = f"{output_path}/output_{projection}_{z}_{x}_{y}.png"

    try:
        # temp_copy_path = f"{input_filename.split('.tif')[0]}_copy_{time.time_ns()}.tif"
        # shutil.copyfile(input_filename, temp_copy_path)
        proc = subprocess.run([
            "gdalwarp",
            input_filename,
            f"{output_path}",
            "-ts", f"{tile_size_x}", f"{tile_size_y}",
            # "-te", f"{xoff}", f"{yoff}", f"{xoff + tile_width}", f"{yoff + tile_height}",
            "-te", format(xoff, 'f'), format(yoff, 'f'), format(xoff + tile_width, 'f'), format(yoff + tile_height, 'f'),
            "-te_srs", srs,
            "-t_srs", srs,
            # "-ot", "Byte",
            "-of", f"{output_type}",
            "-dstalpha",
            "-r", f"{resampling}",
            "-overwrite",
            "-multi"
        ], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # Docs from here: https://gdal.org/en/stable/api/python/utilities.html#osgeo.gdal.Warp
        # ds = gdal.Warp(output_path, input_filename,
        #     options=gdal.WarpOptions(
        #         width=tile_size_x,
        #         height=tile_size_y,
        #         outputBounds=(xoff, yoff, xoff + tile_width, yoff + tile_height),
        #         outputBoundsSRS=srs,
        #         dstSRS=srs,
        #         format=output_type,
        #         dstAlpha=True,
        #         resampleAlg=resampling,
        #         multithread=True
        #     )
        # )
        # del ds

        # Delete temp tiff file:
        # try:
        #     os.remove(temp_copy_path)
        # except:
        #     logging.error(f"-> Error while deleting temp file in geotif2tile:\n{traceback.format_exc()}")

        logging.info(f"Out of gdalwarp: {proc.stdout}")
        if proc.returncode != 0:
            logging.error(f"-> Gdalwarp return non-zero code {proc.returncode}: \n-- ERROR: --\n {proc.stdout}")
            sys.exit(1)
            return None
    except subprocess.CalledProcessError as e:
        logging.error(f"-> Error in cutting geotiff (gdalwarp subprocess): \n-- ERROR: --\n {traceback.format_exc()}")
        sys.exit(1)
        return None
    except:
        logging.error(f"-> Error in cutting geotiff: \n-- ERROR: --\n {traceback.format_exc()}")
        sys.exit(1)
        return None

    # logging.info(f"-> Time of gdalwarp: {time.time() - start_time}")

    start_time = time.time()

    # Ставим opacity:
    # img = Image.open(output_path)
    #
    # # logging.info(f"-> IMG mode: {img.mode}")
    # # logging.info(f"-> IMG size: {img.size}")
    #
    # pixdata = img.load()
    # for y in range(img.size[1]):
    #     for x in range(img.size[0]):
    #         # logging.info(pixdata[x, y])
    #         pix_value = pixdata[x, y]
    #         tuple_len = len(pix_value)
    #         if pix_value[1] != 0:
    #             if to_invert:
    #                 #pixdata[x, y] = (255 - pix_value[0], 128)
    #                 pixdata[x, y] = (255 - pix_value[0], pix_value[1])
    #             else:
    #                 #pixdata[x, y] = (pix_value[0], 128)
    #                 #pixdata[x, y] = (pix_value[0], pix_value[1])
    #
    #                 # color must be int, or tuple of one, three or four elements
    #                 if tuple_len == 4:
    #                     pixdata[x, y] = (pix_value[0], pix_value[1], pix_value[2], pix_value[3])
    #                 else:
    #                     pixdata[x, y] = (pix_value[0], pix_value[1])


    # img.save(output_path, f"{output_type}")

    # delete aux file:
    try:
        os.remove(f"{output_path}.aux.xml")
    except:
        pass

    # logging.info(f"-> Time of alpha putting: {time.time() - start_time}")

    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("input_filename", type=str, help="Input path to geotiff")
    parser.add_argument("output_path", type=str, help="Path to output file (in raster)")

    parser.add_argument("-z", "--zoom", type=int, help="Zoom level of tile", required=True)
    parser.add_argument("-x", type=int, help="X coord of tile. Must be in  range [0, 2^z - 1]", required=True)
    parser.add_argument("-y", type=int, help="Y coord of tile. Must be in  range [0, 2^z - 1]", required=True)
    parser.add_argument("-projection", type=str, help="Projection of result image. Only 'mercator' and 'stereonorth allowed'", choices=["mercator", "stereonorth"], required=True)

    parser.add_argument("-tile_size_x", type=int, help="Tile width of output raster", default=512)
    parser.add_argument("-tile_size_y", type=int, help="Tile height of output raster", default=512)

    parser.add_argument("-output_type", type=str, help="Output type of image", default="PNG", choices=["PNG", "JPEG"])
    parser.add_argument("-resampling", type=str, help="Resampling method", choices=["near", "bilinear", "average"], default="near")

    args = parser.parse_args()

    generate_sat_tile(
        args.input_filename,
        args.output_path,
        args.zoom, args.x, args.y,
        args.projection,
        args.tile_size_x, args.tile_size_y,
        args.output_type,
        args.resampling
    )
