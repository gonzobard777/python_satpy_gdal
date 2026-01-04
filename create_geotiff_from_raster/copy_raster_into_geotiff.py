from typing import Tuple

from osgeo import gdal


def copy_raster_into_geotiff(
        raster_dataset: gdal.Dataset,
        geotiff_dataset: gdal.Dataset,
        preferred_block_size_x: int = 1024,
        preferred_block_size_y: int = 1024,
        min_block_size_y: int = 8,
) -> None:
    """
    Копирует все каналы из raster в geotiff, удерживая в памяти только один чанк данных,
    чтобы не сожрать всю память, когда картинка большая.
    Также переносит NoData, ColorTable и ColorInterpretation.
    """

    width = raster_dataset.RasterXSize
    height = raster_dataset.RasterYSize
    bands = raster_dataset.RasterCount

    block_x, block_y = raster_dataset.GetRasterBand(1).GetBlockSize()
    chunk_x, chunk_y = choose_chunk_size(width, height, block_x, block_y, preferred_block_size_x, preferred_block_size_y, min_block_size_y)
    for i in range(1, bands + 1):
        src = raster_dataset.GetRasterBand(i)
        dst = geotiff_dataset.GetRasterBand(i)
        if src is None or dst is None:
            raise Exception(f"Не удалось получить band {i}")

        nodata = src.GetNoDataValue()
        if nodata is not None:
            dst.SetNoDataValue(nodata)

        color_table = src.GetColorTable()
        if color_table is not None:
            dst.SetColorTable(color_table)

        dst.SetColorInterpretation(src.GetColorInterpretation())

        y = 0
        while y < height:
            ysize = chunk_y if (y + chunk_y) <= height else (height - y)
            x = 0
            while x < width:
                xsize = chunk_x if (x + chunk_x) <= width else (width - x)
                data = src.ReadRaster(x, y, xsize, ysize)
                if data is None:
                    raise Exception(f"ReadRaster вернул None (band={i}, x={x}, y={y}, xsize={xsize}, ysize={ysize})")
                err = dst.WriteRaster(x, y, xsize, ysize, data)
                if err != 0:
                    raise Exception(f"WriteRaster error={err} (band={i}, x={x}, y={y}, xsize={xsize}, ysize={ysize})")
                x += xsize
            y += ysize


def choose_chunk_size(
        width: int, height: int,
        block_x: int, block_y: int,
        preferred_block_size_x: int, preferred_block_size_y: int,
        min_block_size_y: int,
) -> Tuple[int, int]:
    """
    Выбор размера окна чтения/записи:
    - если источник фактически построчный (block_y маленький) — форсируем крупный чанк
    - если источник tiled/блочный — используем родной block size
    """

    if block_x <= 0 or block_y <= 0:
        block_x, block_y = 256, 256

    if block_y <= min_block_size_y:
        chunk_x, chunk_y = preferred_block_size_x, preferred_block_size_y
    else:
        chunk_x, chunk_y = block_x, block_y

    chunk_x = max(1, min(chunk_x, width))
    chunk_y = max(1, min(chunk_y, height))
    return chunk_x, chunk_y
