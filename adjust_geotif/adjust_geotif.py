import sys
import argparse
import logging
logging.basicConfig(level=logging.INFO)
import traceback

from satpy import config, writers
from satpy.scene import Scene

from util.init_scene_data import init_scene_data
from util.save_scene_datasets import save_scene_dataset
from util.gdal_adjust_geotif import gdal_adjust_geotif
from util.tmp_filepath import tmp_filepath

from constant import C
config.set(config_path=[C.CONFIG_DIR])

dataset_id= 'image'
datasets =[dataset_id]


def adjust_geotif(
        input_file_pattern: str,
        output_file: str,
        invert: bool,
        log_prefix: str = "",
) -> None | bool:
    try:
        fnames, reader = init_scene_data(None,None,None,input_file_pattern,log_prefix)

        # satpy использутся по двум причинам:
        #  - при создании сцены выполняется автоматический stretch'инг значений в каналах в диапазон 0-255
        #  - все NoData пиксели делаем прозрачными, см. satpy_config/readers/generic_image.yaml - nodata_handling: nan_mask
        scn = Scene(reader=reader, filenames=fnames)
        scn.load(wishlist=datasets)

        # satpy также имеет встроенные enhance'ры
        if invert:
            tmp_file=tmp_filepath(output_file)
            img = writers.to_image(dataset=scn[dataset_id])
            img.invert()
            img.stretch("linear")
            img.save(tmp_file,fformat='tif',compute=True)
            gdal_adjust_geotif(dataset_id,tmp_file,output_file,remove_src=True,log_prefix=log_prefix)
        else:
            save_scene_dataset(scn, dataset_id, output_file, log_prefix)

    except:
        logging.error(f"| {log_prefix} | Error in adjusting geotiff:\n{traceback.format_exc()}")
        return None

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("input_file_pattern", type=str, help="Pattern to filter file")
    parser.add_argument("output_file", type=str, help="Absolute path to output file")
    parser.add_argument("invert", type=bool, help="Invert channels")
    parser.add_argument("-log_prefix", type=str, default="", help="Log prefix, default empty")

    args = parser.parse_args()

    try:
        res = adjust_geotif(
            input_file_pattern=args.input_file_pattern,
            output_file=args.output_file,
            invert=args.invert,
            log_prefix=args.log_prefix,
        )
        if res is None:
            sys.exit(1)
    except:
        logging.info(f"| {args.log_prefix} | Error in full function \n-- ERROR: --\n {traceback.format_exc()}")
