from util.tmp_filepath import tmp_filepath
from util.gdal_adjust_geotif import gdal_adjust_geotif
from util.remove_existed_file import remove_existed_file

def save_scene_datasets(scn, output_path, datasets, timestamp, log_prefix=''):
    # Проходимся по каждому датасету
    for dataset_id in datasets:

        # Путь до финального файла
        output_file = f"{output_path}-{dataset_id}-{timestamp}.tif"

        save_scene_dataset(scn,dataset_id,output_file,log_prefix)


def save_scene_dataset(scn, dataset_id, output_file, log_prefix=''):
    # Сохраняем датасет во временный geotiff
    tmp_file=tmp_filepath(output_file)
    remove_existed_file(tmp_file)
    scn.save_dataset(dataset_id, filename=tmp_file, writer="geotiff", compute=True)

    # Сооздать результирующий geotiff
    gdal_adjust_geotif(dataset_id,tmp_file,output_file,remove_src=True,log_prefix=log_prefix)