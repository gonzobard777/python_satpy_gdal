import math
from typing import List, Tuple

from osgeo import osr


def compute_geotiff_geotransform(
        left_top_geo: List[float],
        right_top_geo: List[float],
        left_bottom_geo: List[float],
        proj_desc: str,
        width: int,
        height: int,
        tol_rel: float = 1e-3,  # допуск на "квадратность" пикселя (0.1%)
        tol_orth: float = 1e-6,  # допуск ортогональности
) -> Tuple[float, float, float, float, float, float]:
    """
    Строит ПОЛНЫЙ affine GeoTransform по 3 углам растра в WGS84 (lon/lat) и PROJ-строке проекции.

    Углы соответствуют пиксельным координатам:
      - LeftTop     -> (col=0,      row=0)
      - RightTop    -> (col=width,  row=0)
      - LeftBottom  -> (col=0,      row=height)

    Возвращает GeoTransform (gt0..gt5), который сохраняет возможный поворот/скос:
      x = gt0 + col*gt1 + row*gt2
      y = gt3 + col*gt4 + row*gt5

    Проверки:
      1) Изотропность пикселя (почти квадрат): длины шага по X (col) и по Y (row) должны совпадать
      2) Прямой угол между осями растра в проекции: |cos(theta)| <= tol_orth

    Важно:
      - Это аффинная модель. Если картинка на самом деле имеет заметную нелинейную деформацию в проекции,
        3 угла не смогут описать её корректно.
    """

    if width <= 0 or height <= 0:
        raise Exception(f"Некорректный размер растра: width={width}, height={height}. Ожидаются положительные значения.")

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
    xLT, yLT, _ = geo_to_proj.TransformPoint(left_top_geo[0], left_top_geo[1])
    xRT, yRT, _ = geo_to_proj.TransformPoint(right_top_geo[0], right_top_geo[1])
    xLB, yLB, _ = geo_to_proj.TransformPoint(left_bottom_geo[0], left_bottom_geo[1])

    # Вектора одного пикселя в проекции.
    # col_vec: куда и на сколько смещается (x,y), если увеличить col на 1 (движение "вправо" по изображению)
    col_vec_x = (xRT - xLT) / width
    col_vec_y = (yRT - yLT) / width
    # row_vec: куда и на сколько смещается (x,y), если увеличить row на 1 (движение "вниз" по изображению)
    row_vec_x = (xLB - xLT) / height
    row_vec_y = (yLB - yLT) / height

    # Проверка изотропности пикселя (квадратность).
    col_len = math.hypot(col_vec_x, col_vec_y)
    row_len = math.hypot(row_vec_x, row_vec_y)
    if col_len == 0.0 or row_len == 0.0:
        raise Exception("Нулевой размер пикселя (len(col_vec)==0 или len(row_vec)==0). Проверьте углы/проекцию.")
    mean = (col_len + row_len) / 2.0
    rel_diff = abs(col_len - row_len) / mean
    if rel_diff > tol_rel: raise Exception("Размер пикселя не является изотропным (пиксель не квадратный).\n"
                                           f"len(col_vec) = {col_len:.12f}\n"
                                           f"len(row_vec) = {row_len:.12f}\n"
                                           f"Относительное расхождение = {rel_diff:.6g}, допустимо ≤ {tol_rel}")

    # Проверка прямого угла между осями (ортогональность).
    # Для перпендикулярных векторов cos(theta) = 0.
    dot = col_vec_x * row_vec_x + col_vec_y * row_vec_y
    cos_theta_abs = abs(dot) / (col_len * row_len)
    if cos_theta_abs > tol_orth: raise Exception("Оси растра в проекции не образуют прямой угол в пределах допуска.\n"
                                                 f"|cos(theta)| = {cos_theta_abs:.12g}, допустимо ≤ {tol_orth}\n"
                                                 "Проверьте соответствие углов исходному изображению и проекцию, либо ослабьте tol_orth.")
    # Собрать GeoTransform.
    # gt0,gt3 — координаты точки (col=0,row=0) = LeftTop
    # gt1,gt4 — вклад от col (шаг + возможный поворот)
    # gt2,gt5 — вклад от row (шаг + возможный поворот)
    gt0 = xLT
    gt1 = col_vec_x
    gt2 = row_vec_x
    gt3 = yLT
    gt4 = col_vec_y
    gt5 = row_vec_y

    return (gt0, gt1, gt2, gt3, gt4, gt5)
