from typing import List, Tuple
from osgeo import osr

def compute_geotiff_pixelsize(
        left_top_geo: List[float],
        right_top_geo: List[float],
        left_bottom_geo: List[float],
        proj_desc: str,
        width: int,
        height: int,
        tol_rel: float = 1e-3,  # допустимая относительная погрешность изотропности (0.1%)
) -> Tuple[float, float, float]:
    """
    Считает pixel_size GeoTIFF по 3 углам растра и координаты LeftTop.

    Вход:
      - left_top_geo, right_top_geo, left_bottom_geo: [lon, lat] в градусах (WGS84)
      - proj4_desc: строка проекции PROJ
      - width, height: размеры картинки в пикселях
      - tol_rel: относительный допуск на расхождение pixel_size_x и pixel_size_y

    Допущения:
      - координаты углов заданы для УГЛОВ растра:
        LeftTop = (0,0), RightTop = (width,0), LeftBottom = (0,height)

    Возвращает:
      (pixel_size, x_left_top, y_left_top)
    """

    if width <= 0 or height <= 0:
        raise Exception(f"Некорректный размер растра: width={width}, height={height}. "
                        "Ожидаются положительные значения.")

    # WGS84 - World Geodetic System 1984, used in GPS: https://epsg.io/4326
    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG(4326)
    wgs84.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)  # lon,lat → X,Y

    # Целевая СК из PROJ-строки.
    target_srs = osr.SpatialReference()
    target_srs.ImportFromProj4(proj_desc)
    target_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)  # lon,lat → X,Y

    # Конвертер.
    geo_to_proj = osr.CoordinateTransformation(wgs84, target_srs)

    # Спроецировать углы.
    x_left_top, y_left_top, _ = geo_to_proj.TransformPoint(left_top_geo[0], left_top_geo[1])
    x_right_top, y_right_top, _ = geo_to_proj.TransformPoint(right_top_geo[0], right_top_geo[1])
    x_left_bottom, y_left_bottom, _ = geo_to_proj.TransformPoint(left_bottom_geo[0], left_bottom_geo[1])

    # PixelSize.
    pixel_size_x = (x_right_top - x_left_top) / float(width)
    pixel_size_y = (y_left_top - y_left_bottom) / float(height)

    mean = (abs(pixel_size_x) + abs(pixel_size_y)) / 2.0
    if mean == 0.0:
        raise Exception("Вычисленный размер пикселя равен нулю. "
                        "Проверьте координаты углов и параметры проекции.")

    rel_diff = abs(pixel_size_x - pixel_size_y) / mean
    if rel_diff > tol_rel:
        raise Exception("Размер пикселя не является изотропным (пиксель не квадратный).\n"
                        f"pixel_size_x = {pixel_size_x:.12f}\n"
                        f"pixel_size_y = {pixel_size_y:.12f}\n"
                        f"Относительное расхождение = {rel_diff:.6g}, допустимо ≤ {tol_rel}")

    pixel_size = (pixel_size_x + pixel_size_y) / 2.0
    return (pixel_size, x_left_top, y_left_top)
