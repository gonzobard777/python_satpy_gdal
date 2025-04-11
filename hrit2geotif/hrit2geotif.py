import os
import sys
import logging
logging.basicConfig(level=logging.INFO)
import traceback
import argparse
from constant import C
from contract import SatId

from satpy import config
from satpy.scene import Scene

from util.init_scene_data import init_scene_data
from util.save_scene_datasets import save_scene_datasets


def hrit_to_geotiff(
        files_dir: str,
        timestamp: str,
        sat: SatId,
        datasets: list[str],
        output_path: str,
        log_prefix: str = "",
        move_processed_dir: str = ""
) -> str | None:
    try:
        fnames, reader = init_scene_data(sat,files_dir,timestamp,log_prefix)
        if len(fnames) == 0:
            return None

        # Загружаем все файлы HRIT снимка за данное время
        config.set(config_path=[f'{C.CONFIG_DIR}'])
        scn = Scene(reader=reader, filenames=fnames)

        all_datasets = scn.available_dataset_names(composites=True)

        scn.load(wishlist=datasets)
        # scn.load(all_datasets)
        # scn.load(['VIS006'])


        # scn = scn.resample(scn.finest_area(),resampler="nearest")
        # scn.save_dataset(dataset_id='geo_color_high_clouds', )
        # scn.save_dataset(dataset_id='VIS006', )
        # scn.save_dataset(dataset_id='IR1_raw', )
        # scn.save_dataset(dataset_id='B13',writer='simple_image', filename='D:\\del\\python_check\\B13.png')

        # scn = scn.resample(scn.coarsest_area(),resampler="nearest")
        # img = to_image(dataset=scn['B13'])
        # img.invert([True])
        # img.stretch("crude")
        # img.gamma(0.75)
        # img.save('gamma0_75_crude_resampled.png')

        scn = scn.resample(scn.finest_area(), resampler="nearest")  # Ресемпл необходим для некоторых композитов. Без этого работа скрипта не гарантирована!
        save_scene_datasets(scn, output_path, datasets, timestamp, log_prefix)

    except:
        logging.error(f"| {log_prefix} | Error in converting hrit to geotiff by satpy:\n{traceback.format_exc()}")
        return None

    if move_processed_dir == "":
        return output_path

    try:
        for raw_hrit_file in fnames:
            os.replace(raw_hrit_file, os.path.join(move_processed_dir, raw_hrit_file.split("/")[-1]))
    except:
        logging.error(
            f"| {log_prefix} | Error in moving processed hrit files: \n-- ERROR: --\n {traceback.format_exc()}")
        return None

    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("files_dir", type=str, help="Path to dir containing HRIT image")
    parser.add_argument("timestamp", type=str, help="Timestamp of image in format YYYYMMDDHHmm")
    parser.add_argument("sat", type=SatId, help="Satellite Id")
    parser.add_argument("output_path", type=str, help="Path to output geotiff (without .tif postfix)")
    parser.add_argument("datasets", action="extend", nargs="+", type=str,
                        help="list of datasets (composites) needed to proceed")
    parser.add_argument("log_prefix", type=str, default="", help="Log prefix, default empty")
    parser.add_argument("move_processed_dir", type=str, default="",
                        help="Path to dir where to move processed raw hrit files")

    args = parser.parse_args()

    try:
        res = hrit_to_geotiff(
            files_dir=args.files_dir,
            timestamp=args.timestamp,
            sat=args.sat,
            datasets=args.datasets,
            output_path=args.output_path,
            log_prefix=args.log_prefix,
            move_processed_dir=args.move_processed_dir
        )
        if res is None:
            sys.exit(1)
    except:
        logging.info(f"| {args.log_prefix} | Error in full function \n-- ERROR: --\n {traceback.format_exc()}")
