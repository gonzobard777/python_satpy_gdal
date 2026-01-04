from typing import List, Optional

from compute_geotransform import compute_geotransform
from copy_raster import copy_raster
from init import init


def create_geotiff_from_raster(
        proj_desc: str,
        geotiff_path: str,
        raster_path: str,
        raster_lt_geo: List[float],
        raster_rt_geo: List[float],
        raster_lb_geo: List[float],
        geotiff_creation_opts: Optional[List[str]] = None,
) -> None:
    """
    Создает GeoTIFF из входной растровой картинки и геопривязывает его по 3 углам + проекции.

    Аргументы:
      - proj_desc: PROJ-строка целевой проекции (proj.org), например: "+proj=stere +lat_0=90 +lon_0=65 +R=6371008"
      - geotiff_path: путь до результирующего GeoTIFF
      - raster_path: путь до исходной картинки (png/jpg/tif/...)
      - raster_lt_geo, raster_rt_geo, raster_lb_geo: Координаты углов растра, [lon, lat] в градусах (WGS84)
      - geotiff_creation_opts: опции создания GTiff (например ["TILED=YES","COMPRESS=DEFLATE",..])
    """

    # Инициализация:
    #  - создать проекцию
    #  - прочитать растровую картинку
    #  - создать geotiff
    proj, raster_dataset, geotiff_dataset = init(
        proj_desc,
        raster_path,
        geotiff_path,
        geotiff_creation_opts
    )

    # 1. Задать проекцию.
    geotiff_dataset.SetProjection(proj.ExportToWkt())

    # 2. Задать геопривязку картинки.
    geotransform = compute_geotransform(
        proj,
        geotiff_dataset,
        raster_lt_geo,
        raster_rt_geo,
        raster_lb_geo
    )
    geotiff_dataset.SetGeoTransform(geotransform)

    # 3. Скопировать картинку в GeoTIFF.
    copy_raster(raster_dataset, geotiff_dataset)

    # Записать/сбросить на диск.
    geotiff_dataset.FlushCache()

    raster_dataset = None
    geotiff_dataset = None
