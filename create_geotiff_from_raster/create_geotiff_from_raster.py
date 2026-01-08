import argparse
import sys
from typing import List, Optional

from copy_raster_into_geotiff import copy_raster_into_geotiff
from init import init
from pixel_to_proj_converter import pixel_to_proj_converter


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

    # (1) Задать проекцию.
    geotiff_dataset.SetProjection(proj.ExportToWkt())

    # (2) Задать конвертер из Пиксельного пространства -> в пространство Проекции.
    pixel_to_proj = pixel_to_proj_converter(
        proj,
        geotiff_dataset,
        raster_lt_geo,
        raster_rt_geo,
        raster_lb_geo
    )
    # В GDAL этот конвертер почему-то называется GeoTransform.
    geotiff_dataset.SetGeoTransform(pixel_to_proj)

    # (3) Скопировать содержимое растровой картинки внутрь GeoTIFF.
    copy_raster_into_geotiff(raster_dataset, geotiff_dataset)

    # Записать/сбросить на диск.
    geotiff_dataset.FlushCache()

    raster_dataset = None
    geotiff_dataset = None

#-------------------------------

def _parse_lon_lat(value: str) -> List[float]:
    """
    Парсит 'lon,lat' -> [lon, lat]
    """
    try:
        lon, lat = map(float, value.split(","))
        return [lon, lat]
    except Exception:
        raise argparse.ArgumentTypeError(f"Ожидается формат 'lon,lat', получено: {value}")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Создание GeoTIFF из растра с геопривязкой по 3 углам")

    parser.add_argument("--proj", required=True,
                        help='PROJ-строка, например: "+proj=stere +lat_0=90 +lon_0=65 +R=6371008"')

    parser.add_argument("--raster", required=True,
                        help="Путь к исходному растру (png/jpg/tif/...)")

    parser.add_argument("--out", required=True,
                        help="Путь к результирующему GeoTIFF")

    parser.add_argument("--lt", required=True, type=_parse_lon_lat,
                        help="Левый верхний угол (lon,lat)")

    parser.add_argument("--rt", required=True, type=_parse_lon_lat,
                        help="Правый верхний угол (lon,lat)")

    parser.add_argument("--lb", required=True, type=_parse_lon_lat,
                        help="Левый нижний угол (lon,lat)")

    parser.add_argument("--co", action="append", dest="creation_opts",
                        help="Опция создания GeoTIFF (можно указывать несколько раз), "
                             'например: --co TILED=YES --co COMPRESS=DEFLATE')

    args = parser.parse_args(argv)

    create_geotiff_from_raster(
        proj_desc=args.proj,
        geotiff_path=args.out,
        raster_path=args.raster,
        raster_lt_geo=args.lt,
        raster_rt_geo=args.rt,
        raster_lb_geo=args.lb,
        geotiff_creation_opts=args.creation_opts
    )


if __name__ == "__main__":
    main(sys.argv[1:])

# Пример вызова:
# python create_geotiff.py \
#   --proj "+proj=stere +lat_0=90 +lon_0=65 +R=6371008" \
#   --raster input.png \
#   --out output.tif \
#   --lt 30.0,80.0 \
#   --rt 60.0,80.0 \
#   --lb 30.0,70.0 \
#   --co TILED=YES \
#   --co COMPRESS=DEFLATE
