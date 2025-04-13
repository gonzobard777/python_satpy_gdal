import sys
import argparse
import logging
logging.basicConfig(level=logging.INFO)
import traceback

from satpy import config
from satpy.scene import Scene

from util.init_scene_data import init_scene_data
from util.save_scene_datasets import save_scene_dataset

from constant import C
config.set(config_path=[C.CONFIG_DIR])

dataset='image'
datasets =[dataset]

def adjust_geotif(
        input_file_pattern: str,
        output_file: str,
        tmp_output_file: str,
        log_prefix: str = "",
) -> None | bool:
    try:
        fnames, reader = init_scene_data(None,'','',input_file_pattern,log_prefix)
        scn = Scene(reader=reader, filenames=fnames)
        scn.load(wishlist=datasets)
        save_scene_dataset(scn, dataset, output_file, tmp_output_file, log_prefix)
    except:
        logging.error(f"| {log_prefix} | Error in adjusting geotiff:\n{traceback.format_exc()}")
        return None

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("input_file_pattern", type=str, help="Pattern to filter file")
    parser.add_argument("output_file", type=str, help="Absolute path to output file")
    parser.add_argument("tmp_output_file", type=str, help="Absolute path to temporary output file")
    parser.add_argument("-log_prefix", type=str, default="", help="Log prefix, default empty")

    args = parser.parse_args()

    try:
        res = adjust_geotif(
            input_file_pattern=args.input_file_pattern,
            output_file=args.output_file,
            tmp_output_file=args.tmp_output_file,
            log_prefix=args.log_prefix,
        )
        if res is None:
            sys.exit(1)
    except:
        logging.info(f"| {args.log_prefix} | Error in full function \n-- ERROR: --\n {traceback.format_exc()}")
