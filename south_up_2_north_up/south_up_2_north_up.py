import sys
import argparse
import logging
import traceback
import subprocess
logging.basicConfig(level=logging.INFO)

def south_up_2_north_up(input_file,output_file,log_prefix='') -> None | bool:
    try:
        # Перевернуть: был сверху юг -> стал сверху север.
        proc = subprocess.run([
            "gdalwarp",
            "-overwrite",
            "-ct", "+proj=pipeline +step +proj=axisswap +order=1,2",
            "-of", "GTiff",
            input_file,
            output_file,
        ], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        if proc.returncode == 0:
            logging.info(f"| {log_prefix} | axisswap done")
        else:
            logging.error(f"| {log_prefix} | axisswap return non-zero code {proc.returncode}: \n-- ERROR: --\n {proc.stdout}")
    except:
        logging.error(f"| {log_prefix} | Error while axisswap: {input_file}")
        return None

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("input_file", type=str, help="файл, содержимое которого надо перевернуть")
    parser.add_argument("output_file", type=str, help="файл приемник, куда будет записан результат переворота")
    parser.add_argument("-log_prefix", type=str, default="", help="Log prefix, default empty")

    args = parser.parse_args()

    try:
        res = south_up_2_north_up(
            input_file=args.input_file,
            output_file=args.output_file,
            log_prefix=args.log_prefix,
        )
        if res is None:
            sys.exit(1)
    except:
        logging.info(f"| {args.log_prefix} | Error in full function \n-- ERROR: --\n {traceback.format_exc()}")
