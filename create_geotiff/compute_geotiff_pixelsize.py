from typing import List, Tuple

from osgeo import osr


def compute_geotiff_pixelsize(
        left_top_geo: List[float],
        right_top_geo: List[float],
        left_bottom_geo: List[float],
        proj_desc: str,
        width: int,
        height: int,
        tol_rel: float = 1e-3,  # допустимая относительная погрешность изотропности пикселя (0.1%)
) -> Tuple[float, float, float]:
    """
    Считает pixel_size GeoTIFF по 3 углам растра и координаты LeftTop.

    Вход:
      - left_top_geo, right_top_geo, left_bottom_geo: Координаты углов растра, [lon, lat] в градусах (WGS84)
      - proj_desc: строка проекции PROJ
      - width, height: размеры картинки в пикселях
      - tol_rel: относительный допуск на расхождение pixel_size_x и pixel_size_y

    Допущения:
      - координаты углов заданы для УГЛОВ растра:
        LeftTop = (0,0), RightTop = (width,0), LeftBottom = (0,height)
      - ось Y проекции, описанной proj_desc, направлена вверх

    Возвращает:
      (pixel_size, x_left_top, y_left_top)
    """

    if width <= 0 or height <= 0:
        raise Exception(f"Некорректный размер растра: width={width}, height={height}. "
                        "Ожидаются положительные значения.")

    # WGS84 - World Geodetic System 1984, used in GPS: https://epsg.io/4326
    wgs84 = osr.SpatialReference()
    if wgs84.ImportFromEPSG(4326) != 0: raise Exception("Не удалось создать SRS EPSG:4326 (WGS84).")
    wgs84.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)  # lon,lat → X,Y

    # Целевая СК из PROJ-строки.
    target_srs = osr.SpatialReference()
    if target_srs.ImportFromProj4(proj_desc) != 0: raise Exception(f"Не удалось создать SRS из PROJ-строки:\n{proj_desc}")
    target_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)  # lon,lat → X,Y

    # Конвертер.
    geo_to_proj = osr.CoordinateTransformation(wgs84, target_srs)
    if geo_to_proj is None: raise Exception("Не удалось создать преобразование координат (geo -> to proj)")

    # Спроецировать углы.
    x_left_top, y_left_top, _ = geo_to_proj.TransformPoint(left_top_geo[0], left_top_geo[1])
    x_right_top, y_right_top, _ = geo_to_proj.TransformPoint(right_top_geo[0], right_top_geo[1])
    x_left_bottom, y_left_bottom, _ = geo_to_proj.TransformPoint(left_bottom_geo[0], left_bottom_geo[1])
    if y_left_bottom >= y_left_top: raise Exception(f"Неожиданное направление оси Y проекции: y_left_bottom ({y_left_bottom}) >= Y_left_top ({y_left_top}). "
                                                    "Проверьте порядок углов и параметры проекции.")
    # PixelSize на плоскости проекции в метрах.
    pixel_size_x = (x_right_top - x_left_top) / width
    pixel_size_y = (y_left_top - y_left_bottom) / height

    # Проверить изотропность пикселя -> Шаг по X и шаг по Y должны быть одинаковыми (по модулю).
    mean = (abs(pixel_size_x) + abs(pixel_size_y)) / 2.0  # Нормировочный коэффициент для проверки относительной ошибки.
    if mean == 0.0: raise Exception("Вычисленный размер пикселя равен нулю. "
                                    "Проверьте координаты углов и параметры проекции.")
    rel_diff = abs(pixel_size_x - pixel_size_y) / mean
    if rel_diff > tol_rel:
        raise Exception("Размер пикселя не является изотропным (пиксель не квадратный).\n"
                        f"pixel_size_x = {pixel_size_x:.12f}\n"
                        f"pixel_size_y = {pixel_size_y:.12f}\n"
                        f"Относительное расхождение = {rel_diff:.6g}, допустимо ≤ {tol_rel}")

    pixel_size = (pixel_size_x + pixel_size_y) / 2.0
    return (pixel_size, x_left_top, y_left_top)
