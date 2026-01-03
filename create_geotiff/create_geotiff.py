import os
from typing import List, Optional

from osgeo import gdal, osr

from compute_geotiff_pixelsize import compute_geotiff_pixelsize
from copy_raster_bands_blockwise import copy_raster_bands_blockwise


def create_geotiff(
        input_raster_path: str,
        output_geotiff_path: str,
        left_top_geo: List[float],
        right_top_geo: List[float],
        left_bottom_geo: List[float],
        proj_desc: str,
        creation_options: Optional[List[str]] = None,
) -> None:
    """
    Создает GeoTIFF из входной растровой картинки и геопривязывает его по 3 углам + проекции.

    Аргументы:
      - input_raster_path: путь до исходной картинки (png/jpg/tif/...)
      - output_geotiff_path: путь до результирующего GeoTIFF
      - left_top_geo, right_top_geo, left_bottom_geo: Координаты углов растра, [lon, lat] в градусах (WGS84)
      - proj_desc: PROJ-строка целевой проекции (proj.org), например: "+proj=stere +lat_0=90 +lon_0=65 +R=6371008"
      - creation_options: опции создания GTiff (например ["TILED=YES","COMPRESS=DEFLATE"])
    """

    if creation_options is None:
        creation_options = [
            "TILED=YES",  # Хранить данные ВНУТРИ одного GeoTIFF тайлами (эффективное оконное чтение, быстрее gdalwarp)
            "COMPRESS=DEFLATE",  # Lossless-сжатие: уменьшает размер файла без потери данных
            "PREDICTOR=2"  # Улучшает сжатие DEFLATE (Записывается не абсолютное значение пикселя, а разность с предыдущим по X)
        ]

    src = gdal.Open(input_raster_path, gdal.GA_ReadOnly)
    if src is None: raise Exception(f"Не удалось открыть входной растр: {input_raster_path}")

    width = src.GetRasterXSize()
    height = src.GetRasterYSize()
    if width <= 0 or height <= 0: raise Exception(f"Некорректный размер входного растра: width={width}, height={height}")

    # Количество каналов (band'ов):
    #   1  → grayscale
    #   3  → RGB         RGB PNG/JPEG
    #   4  → RGBA        RGBA PNG, CMYK JPEG
    #   N  → произвольное многоканальное изображение
    bands = src.RasterCount
    if bands <= 0: raise Exception("Входной файл не содержит raster band'ов")

    # Тип данных одного пикселя (берём из первого band'а, обычно одинаковый для всех band'ов):
    #   gdal.GDT_Byte     → uint8
    #   gdal.GDT_UInt16   → uint16
    #   gdal.GDT_Int16    → int16
    #   gdal.GDT_UInt32   → uint32
    #   gdal.GDT_Int32    → int32
    #   gdal.GDT_Float32 → float32
    #   gdal.GDT_Float64 → float64
    first_band = src.GetRasterBand(1)
    if first_band is None: raise Exception("Не удалось получить первый band входного растра")
    dtype = first_band.DataType

    # Посчитать pixel_size и координаты левого верхнего угла в метрах целевой проекции.
    pixel_size, x_left_top, y_left_top = compute_geotiff_pixelsize(
        left_top_geo=left_top_geo,
        right_top_geo=right_top_geo,
        left_bottom_geo=left_bottom_geo,
        proj_desc=proj_desc,
        width=width,
        height=height)

    # Создать GeoTIFF.
    driver = gdal.GetDriverByName("GTiff")
    if driver is None: raise Exception("Не найден драйвер GDAL 'GTiff'.")
    if os.path.exists(output_geotiff_path):  # Удалить существующий файл, если есть.
        try:
            driver.Delete(output_geotiff_path)
        except Exception:
            os.remove(output_geotiff_path)

    dst = driver.Create(
        output_geotiff_path,
        width,
        height,
        bands,
        dtype,
        options=creation_options)
    if dst is None: raise Exception(f"Не удалось создать GeoTIFF: {output_geotiff_path}")

    # Геотрансформ: (originX, pixelWidth, rotX, originY, rotY, pixelHeight).
    # В проекции Y направлена вверх, но в растре строки идут вниз => pixelHeight должен быть отрицательным.
    geotransform = (x_left_top, pixel_size, 0.0, y_left_top, 0.0, -pixel_size)
    dst.SetGeoTransform(geotransform)

    # Проекция из PROJ-строки -> WKT.
    target_srs = osr.SpatialReference()
    if target_srs.ImportFromProj4(proj_desc) != 0: raise Exception(f"Не удалось создать SRS из PROJ-строки:\n{proj_desc}")
    target_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    dst.SetProjection(target_srs.ExportToWkt())

    # Копирование данных по бандам (блочно), чтобы не съесть доступную RAM.
    copy_raster_bands_blockwise(src, dst)

    # Записать/сбросить на диск
    dst.FlushCache()
    dst = None
    src = None
