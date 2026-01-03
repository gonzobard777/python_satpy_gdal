from osgeo import gdal


def copy_raster(
        raster_dataset: gdal.Dataset,
        geotiff_dataset: gdal.Dataset,
        preferred_block_size_x: int = 1024,
        preferred_block_size_y: int = 1024,
        min_block_size_y: int = 8,
) -> None:
    """
    Копирует все band'ы из raster в geotiff, удерживая в RAM только один чанк данных.
    Также переносит NoData, ColorTable и ColorInterpretation.
    """

    width = raster_dataset.RasterXSize
    height = raster_dataset.RasterYSize
    bands = raster_dataset.RasterCount

    block_x, block_y = raster_dataset.GetRasterBand(1).GetBlockSize()
    chunk_x, chunk_y = choose_chunk_size(width, height, block_x, block_y, preferred_block_size_x, preferred_block_size_y, min_block_size_y)
    for i in range(1, bands + 1):
        src_band = raster_dataset.GetRasterBand(i)
        dst_band = geotiff_dataset.GetRasterBand(i)
        if src_band is None or dst_band is None: raise Exception(f"Не удалось получить band {i}")

        nodata = src_band.GetNoDataValue()
        if nodata is not None: dst_band.SetNoDataValue(nodata)

        color_table = src_band.GetColorTable()
        if color_table is not None: dst_band.SetColorTable(color_table)
        dst_band.SetColorInterpretation(src_band.GetColorInterpretation())

        y = 0
        while y < height:
            ysize = chunk_y if (y + chunk_y) <= height else (height - y)
            x = 0
            while x < width:
                xsize = chunk_x if (x + chunk_x) <= width else (width - x)
                data = src_band.ReadRaster(x, y, xsize, ysize)
                if data is None:
                    raise Exception(f"ReadRaster вернул None (band={i}, x={x}, y={y}, xsize={xsize}, ysize={ysize})")

                err = dst_band.WriteRaster(x, y, xsize, ysize, data)
                if err != 0:
                    raise Exception(f"WriteRaster error={err} (band={i}, x={x}, y={y}, xsize={xsize}, ysize={ysize})")

                x += xsize
            y += ysize


def choose_chunk_size(
        width: int,
        height: int,
        block_x: int,
        block_y: int,
        preferred_block_size_x: int,
        preferred_block_size_y: int,
        min_block_size_y: int,
) -> tuple[int, int]:
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
