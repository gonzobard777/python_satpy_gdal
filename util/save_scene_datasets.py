import os
import logging
logging.basicConfig(level=logging.INFO)
import subprocess
import traceback

def save_scene_datasets(scn, output_path, datasets, timestamp, log_prefix):
    # Проходимся по каждому датасету
    for dataset in datasets:
        filename_path=f"{output_path}-{dataset}-{timestamp}"
        # Путь до финального файла
        output_file = f"{filename_path}.tif"
        # Временный выходной файл после scn.save_dataset. Далее, он преобразуется с помощью gdal_translate
        tmp_file = f"{filename_path}_temp.tif"

        save_scene_dataset(scn, dataset, output_file, tmp_file, log_prefix)


def save_scene_dataset(scn, dataset, output_file, tmp_output_file, log_prefix):
    try:
        if os.path.exists(tmp_output_file):
            os.remove(tmp_output_file)

        # Сохраняем во временный файл
        scn.save_dataset(dataset, filename=tmp_output_file, writer="geotiff", compute=True)

        # Конвертируем с помощью gdal_translate, чтобы geotiff не был битым
        proc = subprocess.run([
            "gdal_translate",
            tmp_output_file,
            output_file,
            "-of", f"GTiff",
        ], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        if proc.returncode == 0:
            logging.info(f"| {log_prefix} | scene dataset saved: {dataset}, {output_file}")
        else:
            # Если gdal_translate произошел с ошибкой
            logging.error(f"| {log_prefix} | gdal_translate return non-zero code {proc.returncode}: \n-- ERROR: --\n {proc.stdout}")
    except:
        logging.error(f"| {log_prefix} | Error in saving dataset: {dataset}:\n{traceback.format_exc()}")
    finally:
        if os.path.exists(tmp_output_file):
            os.remove(tmp_output_file)
