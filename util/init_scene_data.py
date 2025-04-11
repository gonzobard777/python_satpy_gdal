import glob
import logging
from itertools import product
from datetime import datetime, timedelta
from contract import SatId


def init_scene_data(
    sat: SatId,
    files_dir: str,
    timestamp: str,
    log_prefix: str = '',
) -> tuple[list[str], str]:

    fnames=[]
    reader=''

    if sat == SatId.MSG2:
        filter_name = f"{files_dir}/H*MSG2*{timestamp}*__"
        fnames = glob.glob(filter_name)
        reader = 'seviri_l1b_hrit'
    elif sat == SatId.MSG3:
        filter_name = f"{files_dir}/H*MSG3*{timestamp}*__"
        fnames = glob.glob(filter_name)
        reader = 'seviri_l1b_hrit'
    elif sat == SatId.Himawari:
        timestamp_dt = datetime.strptime(timestamp, "%Y%m%d%H%M")
        fnames = []
        for x1, x2 in product(range(10), range(10)):
            segment_str = str(x1 + 1)
            segment_str = "0" * (2 - len(segment_str)) + segment_str
            pattern=f"{files_dir}/IMG_DK*{(timestamp_dt + timedelta(minutes=x2)).strftime('%Y%m%d%H%M')}_0{segment_str}"
            fnames.extend(glob.glob(pattern))
        reader = 'ahi_hrit'
    else:
        logging.error(f"| {log_prefix} | Wrong sat_id: {sat}")


    if len(fnames) == 0:
        logging.info(f"| {log_prefix} | No such files mathing pattern")
    else:
        logging.info(f"| {log_prefix} | -> count of files: {len(fnames)}, timestamp:{timestamp}")

    return fnames, reader
