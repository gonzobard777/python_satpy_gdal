import os
import logging
import subprocess
import traceback

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
