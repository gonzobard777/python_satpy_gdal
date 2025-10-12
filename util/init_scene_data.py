import os
import glob
import logging
logging.basicConfig(level=logging.INFO)
import warnings
warnings.filterwarnings("ignore")
from itertools import product
from datetime import datetime, timedelta
from contract import SatId


def init_scene_data(
        sat: SatId,
        timestamp: str,
        files_dir: str,
        generic_image_pattern: None | str = None,
        log_prefix: str = '',
) -> tuple[list[str], str]:

    dir_list = os.listdir(files_dir)
    logging.info(f"| {log_prefix} | всего файлов {len(dir_list)} | в папке: {files_dir} ")

    fnames=[]
    reader=''

    if sat == SatId.MSG2: # HRIT
        pattern = f"{files_dir}/H*MSG2*{timestamp}*__"
        fnames = glob.glob(pattern)
        reader = 'seviri_l1b_hrit'
    elif sat == SatId.MSG3: # HRIT
        pattern = f"{files_dir}/H*MSG3*{timestamp}*__"
        fnames = glob.glob(pattern)
        reader = 'seviri_l1b_hrit'
    elif sat == SatId.Himawari: # HRIT
        timestamp_dt = datetime.strptime(timestamp, "%Y%m%d%H%M")
        fnames = []
        for x1, x2 in product(range(10), range(10)):
            segment_str = str(x1 + 1)
            segment_str = "0" * (2 - len(segment_str)) + segment_str
            pattern=f"{files_dir}/IMG_DK*{(timestamp_dt + timedelta(minutes=x2)).strftime('%Y%m%d%H%M')}_0{segment_str}"
            fnames.extend(glob.glob(pattern))
        reader = 'ahi_hrit'
    elif generic_image_pattern is not None: # Произвольный файл. Обычно GeoTIFF
        fnames = glob.glob(generic_image_pattern)
        reader = 'generic_image'
    else:
        logging.error(f"| {log_prefix} | Unknown sat_id: {sat}")

    if len(fnames) == 0:
        logging.info(f"| {log_prefix} | No such files mathing pattern")
    else:
        logging.info(f"| {log_prefix} | -> count of files: {len(fnames)}, timestamp:{timestamp}")
        for abs_path in fnames:
            logging.info(f"| {log_prefix} |    - {abs_path}")

    return fnames, reader
