import math
from typing import List, Tuple

from osgeo import gdal, osr
from osgeo.osr import SpatialReference


def compute_geotransform(
        proj: SpatialReference,
        geotiff_dataset: gdal.Dataset,
        raster_lt_geo: List[float],  # Угловые точки
        raster_rt_geo: List[float],  # растровой картинки
        raster_lb_geo: List[float],  # в гео-координатах.
        tol_rel: float = 1e-3,  # Допуск на "квадратность" пикселя (0.1%).
        tol_ort: float = 1e-6,  # Допуск ортогональности.
) -> Tuple[float, float, float, float, float, float]:
    """
    Строит ПОЛНЫЙ affine GeoTransform по 3 углам растра в WGS84 (lon/lat) и PROJ-строке проекции.

    Семантика углов: outer corners (границы пиксельной сетки).
    Гео-координаты углов растра соответствуют координатам УЗЛОВ пиксельной сетки, а не центров пикселей:
      - raster_lt_geo -> (col=0, row=0) = LeftTop узел пиксельной сетки
                                        = LeftTop угол пикселя [0,0]

      - raster_rt_geo -> (col=W, row=0) = RightTop узел пиксельной сетки
                                        = RightTop угол пикселя [W-1,0]

      - raster_lb_geo -> (col=0, row=H) = LeftBottom узел пиксельной сетки
                                        = LeftBottom угол пикселя [0,H-1]

    На примере для W=2, H=2. Здесь [col,row] - индексы узлов пиксельной сетки.

        [0,0] ── [1,0] ── [2,0]        LT [0,0] ───────── [2,0] RT
          │        │        │               │               │
        [0,1] ── [1,1] ── [2,1]    =>       │               │
          │        │        │               │               │
        [0,2] ── [1,2] ── [2,2]        LB [0,2] ───────── [2,2] RB


    Возвращает GeoTransform (gt0..gt5), который сохраняет возможный поворот/скос:
      x = gt0 + col*gt1 + row*gt2
      y = gt3 + col*gt4 + row*gt5

    Проверки:
      1) Изотропность пикселя (почти квадрат): длины шага по X (col) и по Y (row) должны совпадать
      2) Прямой угол между осями растра в проекции: |cos(theta)| <= tol_ort

    Важно:
      - Это аффинная модель. Если картинка на самом деле имеет заметную нелинейную деформацию в проекции,
        3 угла не смогут описать её корректно.
    """

    # WGS84 - World Geodetic System 1984, used in GPS: https://epsg.io/4326
    geo = osr.SpatialReference()
    if geo.ImportFromEPSG(4326) != 0:
        raise Exception("Не удалось создать SRS EPSG:4326 (WGS84).")
    geo.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)  # lon,lat → X,Y

    # Конвертер.
    geo_to_proj = osr.CoordinateTransformation(geo, proj)
    if geo_to_proj is None: raise Exception("Не удалось создать конвертер geo_to_proj")

    # Спроецировать углы растра.
    xLT, yLT, _ = geo_to_proj.TransformPoint(raster_lt_geo[0], raster_lt_geo[1])
    xRT, yRT, _ = geo_to_proj.TransformPoint(raster_rt_geo[0], raster_rt_geo[1])
    xLB, yLB, _ = geo_to_proj.TransformPoint(raster_lb_geo[0], raster_lb_geo[1])

    width = geotiff_dataset.RasterXSize
    height = geotiff_dataset.RasterYSize
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
    if cos_theta_abs > tol_ort: raise Exception("Оси растра в проекции не образуют прямой угол в пределах допуска.\n"
                                                f"|cos(theta)| = {cos_theta_abs:.12g}, допустимо ≤ {tol_ort}\n"
                                                "Проверьте соответствие углов исходному изображению и проекцию, либо ослабьте tol_ort.")
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
