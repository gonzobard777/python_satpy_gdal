from typing import List, Optional

from compute_geotiff_geotransform import compute_geotiff_geotransform
from copy_raster import copy_raster
from init import init


def create_geotiff(
        geotiff_path: str,
        raster_path: str,
        raster_lt_geo: List[float],
        raster_rt_geo: List[float],
        raster_lb_geo: List[float],
        proj_desc: str,
        geotiff_creation_opts: Optional[List[str]] = None,
) -> None:
    """
    Создает GeoTIFF из входной растровой картинки и геопривязывает его по 3 углам + проекции.

    Аргументы:
      - geotiff_path: путь до результирующего GeoTIFF
      - raster_path: путь до исходной картинки (png/jpg/tif/...)
      - raster_lt_geo, raster_rt_geo, raster_lb_geo: Координаты углов растра, [lon, lat] в градусах (WGS84)
      - proj_desc: PROJ-строка целевой проекции (proj.org), например: "+proj=stere +lat_0=90 +lon_0=65 +R=6371008"
      - geotiff_creation_opts: опции создания GTiff (например ["TILED=YES","COMPRESS=DEFLATE",..])
    """

    # Инициализация.
    proj, raster_dataset, geotiff_dataset = init(
        proj_desc,
        raster_path,
        geotiff_path,
        geotiff_creation_opts
    )

    # Задать проекцию.
    geotiff_dataset.SetProjection(proj.ExportToWkt())

    # Задать геопривязку картинки.
    geotransform = compute_geotiff_geotransform(
        proj,
        geotiff_dataset,
        raster_lt_geo,
        raster_rt_geo,
        raster_lb_geo
    )
    geotiff_dataset.SetGeoTransform(geotransform)

    # Скопировать картинку.
    copy_raster(raster_dataset, geotiff_dataset)

    # Записать/сбросить на диск.
    geotiff_dataset.FlushCache()

    raster_dataset = None
    geotiff_dataset = None
