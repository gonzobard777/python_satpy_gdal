import os
from typing import List, Optional, Tuple

from osgeo import gdal, osr
from osgeo.osr import SpatialReference


def init(
        proj_desc: str,
        raster_path: str,
        geotiff_path: str,
        geotiff_creation_opts: Optional[List[str]] = None,
) -> Tuple[SpatialReference, gdal.Dataset, gdal.Dataset]:
    # Создать проекцию по описанию.
    proj = osr.SpatialReference()
    if proj.ImportFromProj4(proj_desc) != 0:
        raise Exception(f"Не удалось создать проекцию по описанию:\n{proj_desc}")

    # Открыть растровую картинку.
    raster_dataset = gdal.Open(raster_path, gdal.GA_ReadOnly)
    if raster_dataset is None:
        raise Exception(f"Не удалось открыть входной растр: {raster_path}")

    width = raster_dataset.RasterXSize
    height = raster_dataset.RasterYSize
    if width <= 0 or height <= 0:
        raise Exception(f"Некорректный размер входного растра: width={width}, height={height}")

    # Количество каналов (band'ов):
    #   1  → grayscale
    #   3  → RGB         RGB PNG/JPEG
    #   4  → RGBA        RGBA PNG, CMYK JPEG
    #   N  → произвольное многоканальное изображение
    bands = raster_dataset.RasterCount
    if bands <= 0:
        raise Exception("Входной файл не содержит raster band'ов")

    # Тип данных одного пикселя (берём из первого band'а, обычно одинаковый для всех band'ов):
    #   gdal.GDT_Byte    → uint8
    #   gdal.GDT_UInt16  → uint16
    #   gdal.GDT_Int16   → int16
    #   gdal.GDT_UInt32  → uint32
    #   gdal.GDT_Int32   → int32
    #   gdal.GDT_Float32 → float32
    #   gdal.GDT_Float64 → float64
    first_band = raster_dataset.GetRasterBand(1)
    if first_band is None:
        raise Exception("Не удалось получить первый band входного растра")

    # Удалить существующий GeoTIFF-файл, если есть.
    if os.path.exists(geotiff_path):
        os.remove(geotiff_path)

    driver = gdal.GetDriverByName("GTiff")
    if driver is None:
        raise Exception("Не найден драйвер GDAL 'GTiff'.")

    if geotiff_creation_opts is None:
        geotiff_creation_opts = [
            "TILED=YES",  # Хранить данные ВНУТРИ одного GeoTIFF тайлами (эффективное оконное чтение)
            "COMPRESS=DEFLATE",  # Lossless-сжатие: уменьшает размер файла без потери данных
            "PREDICTOR=2"  # Улучшает сжатие DEFLATE (Записывается не абсолютное значение пикселя, а разность с предыдущим по X)
        ]

    # Создать GeoTIFF.
    geotiff_dataset = driver.Create(
        geotiff_path,
        width,
        height,
        bands,
        first_band.DataType,
        options=geotiff_creation_opts
    )
    if geotiff_dataset is None:
        raise Exception(f"Не удалось создать GeoTIFF: {geotiff_path}")
    if geotiff_dataset.RasterXSize != width or geotiff_dataset.RasterYSize != height:
        raise Exception("raster/geotiff имеют разные размеры")
    if geotiff_dataset.RasterCount != bands:
        raise Exception("raster/geotiff имеют разное число band'ов")

    return (proj, raster_dataset, geotiff_dataset)
