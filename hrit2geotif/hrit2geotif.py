import os
import sys
import logging
logging.basicConfig(level=logging.INFO)
import traceback
import argparse
import subprocess
from constant import C

from satpy import config
from satpy.scene import Scene

from datetime import datetime, timedelta
from itertools import product
import glob


def save_scene_datasets(scn, output_path, datasets, timestamp, log_prefix):
    # Проходимся по каждому датасету
    for dataset in datasets:
        # Временный выходной файл после scn.save_dataset. Далее, он преобразуется с помощью gdal_translate
        dataset_temp_output_path = f"{output_path}-{dataset}-{timestamp}_temp.tif"
        # Путь до финального файла
        dataset_output_path = f"{output_path}-{dataset}-{timestamp}.tif"

        try:
            if os.path.exists(dataset_temp_output_path):
                os.remove(dataset_temp_output_path)

            # Сохраняем во временный файл
            scn.save_dataset(dataset, filename=dataset_temp_output_path, writer="geotiff", compute=True)
            logging.info(f"| {log_prefix} | scene dataset saved: {dataset}, {dataset_temp_output_path}")

            # Конвертируем с помощью gdal_translate, чтобы geotiff не был битым
            proc = subprocess.run([
                "gdal_translate",
                dataset_temp_output_path,
                dataset_output_path,
                "-of", f"GTiff",
            ], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            # Если gdal_translate произошел с ошибкой
            if proc.returncode != 0:
                logging.error(
                    f"| {log_prefix} | gdal_translate return non-zero code {proc.returncode}: \n-- ERROR: --\n {proc.stdout}")
        except:
            logging.error(f"| {log_prefix} | Error in saving dataset: {dataset}:\n{traceback.format_exc()}")
        finally:
            if os.path.exists(dataset_temp_output_path):
                os.remove(dataset_temp_output_path)


def hrit_to_geotiff(
        hrit_image_dir: str,
        timestamp: str, sat_id: int, datasets: list[str],
        output_path: str,
        log_prefix: str = "",
        move_processed_dir: str = ""
) -> str | None:
    try:

        if sat_id == 1:
            filter_name = f"{hrit_image_dir}/H*MSG2*{timestamp}*__"
            fnames = glob.glob(filter_name)
            reader = 'seviri_l1b_hrit'
        elif sat_id == 2:
            filter_name = f"{hrit_image_dir}/H*MSG3*{timestamp}*__"
            fnames = glob.glob(filter_name)
            reader = 'seviri_l1b_hrit'
        elif sat_id == 3:
            timestamp_dt = datetime.strptime(timestamp, "%Y%m%d%H%M")
            fnames = []
            for x1, x2 in product(range(10), range(10)):
                segment_str = str(x1 + 1)
                segment_str = "0" * (2 - len(segment_str)) + segment_str
                pattern=f"{hrit_image_dir}/IMG_DK*{(timestamp_dt + timedelta(minutes=x2)).strftime('%Y%m%d%H%M')}_0{segment_str}"
                fnames.extend(glob.glob(pattern))
            reader = 'ahi_hrit'
        else:
            logging.error(f"| {log_prefix} | Wrong sat_id: {sat_id}")
            return None

        logging.info(f"| {log_prefix} | -> count of files: {len(fnames)}, timestamp:{timestamp}")
        if len(fnames) == 0:
            logging.info(f"| {log_prefix} | No such files mathing pattern")
            return None

        # Загружаем все файлы HRIT снимка за данное время
        # config.set(config_path=[f'{C.CONFIG_DIR}'])
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

    parser.add_argument("hrit_dir", type=str, help="Path to dir containing HRIT image")
    parser.add_argument("timestamp", type=str, help="Timestamp of image in format YYYYMMDDHHmm")
    parser.add_argument("sat_id", type=int, help="Type of sat (1 - MSG2, 2 - MSG3, 3 - Himawari)")
    parser.add_argument("output_path", type=str, help="Path to output geotiff (without .tif postfix)")
    parser.add_argument("-datasets", action="extend", nargs="+", type=str,
                        help="list of datasets (composites) needed to proceed")
    parser.add_argument("-log_prefix", type=str, default="", help="Log prefix, default empty")
    parser.add_argument("-move_processed_dir", type=str, default="",
                        help="Path to dir where to move processed raw hrit files")

    args = parser.parse_args()

    try:
        res = hrit_to_geotiff(
            hrit_image_dir=args.hrit_dir,
            timestamp=args.timestamp,
            sat_id=args.sat_id,
            datasets=args.datasets,
            output_path=args.output_path,
            log_prefix=args.log_prefix,
            move_processed_dir=args.move_processed_dir
        )
        if res is None:
            sys.exit(1)
    except:
        logging.info(f"| {args.log_prefix} | Error in full function \n-- ERROR: --\n {traceback.format_exc()}")
