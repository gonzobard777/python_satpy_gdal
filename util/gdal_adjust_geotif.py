import os
import logging
logging.basicConfig(level=logging.INFO)
import subprocess
import traceback
from util.remove_existed_file import remove_existed_file

def gdal_adjust_geotif(
        dataset_id,
        src_file,
        dst_file,
        remove_src=False,
        log_prefix=''):

    logging.info(f"| {log_prefix} | gdal_translate, файл: {src_file} | exists: {os.path.exists(src_file)}")

    try:
        # Конвертируем с помощью gdal_translate, чтобы geotiff не был битым
        proc = subprocess.run([
            "gdal_translate",
            src_file,
            dst_file,
            "-of", "GTiff",
            "-co", "COMPRESS=LZW",
            "-co", "PREDICTOR=2",
        ], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        if proc.returncode == 0:
            logging.info(f"| {log_prefix} | dataset saved: {dataset_id}, {dst_file}")
        else:
            # Если gdal_translate произошел с ошибкой
            logging.error(f"| {log_prefix} | gdal_translate return non-zero code {proc.returncode}: \n-- ERROR: --\n {proc.stdout}")
    except:
        logging.error(f"| {log_prefix} | Error in saving dataset: {dataset_id}:\n{traceback.format_exc()}")
    finally:
        if remove_src:
            remove_existed_file(src_file)
