"""
Spiral Line Art Generator.
Изображение рисуется одной непрерывной спиралью переменной толщины.
Тёмные участки = толстая линия, светлые = тонкая.
"""

import numpy as np
from PIL import Image, ImageDraw
import argparse
import math


def load_and_preprocess(image_path, target_width=800):
    """Загружает изображение и приводит к нужному размеру."""
    img = Image.open(image_path).convert("L")  # оттенки серого
    ratio = target_width / img.width
    new_size = (target_width, int(img.height * ratio))
    img = img.resize(new_size, Image.LANCZOS)
    return np.array(img, dtype=np.float32)


def generate_spiral_path(width, height, num_turns=50, spacing_factor=1.0):
    """
    Генерирует путь спирали, заполняющей прямоугольник.
    
    width: ширина изображения
    height: высота изображения
    num_turns: количество витков спирали
    spacing_factor: множитель расстояния между витками
    
    Возвращает список точек [(x1, y1), (x2, y2), ...]
    """
    cx, cy = width / 2, height / 2
    
    # Радиусы спирали подгоняем под размер изображения
    max_radius_x = width / 2 * 0.95
    max_radius_y = height / 2 * 0.95
    
    points = []
    
    for i in range(num_turns * 100):  # 100 точек на виток
        t = i / 100.0
        
        # Угол увеличивается линейно
        angle = t * 2 * math.pi
        
        # Радиус растёт линейно от центра к краям
        r_progress = t / num_turns
        
        # Эллиптическая спираль
        rx = max_radius_x * r_progress
        ry = max_radius_y * r_progress
        
        x = cx + rx * math.cos(angle)
        y = cy + ry * math.sin(angle)
        
        points.append((x, y))
    
    return points


def get_line_thickness(gray_array, x, y, min_thick=0.5, max_thick=6.0):
    """
    Определяет толщину линии в точке (x, y) на основе яркости.
    
    gray_array: массив яркостей (0=чёрный, 255=белый)
    min_thick: минимальная толщина (для светлых участков)
    max_thick: максимальная толщина (для тёмных участков)
    """
    h, w = gray_array.shape
    
    # Округляем координаты
    xi = int(min(max(0, x), w - 1))
    yi = int(min(max(0, y), h - 1))
    
    # Берём яркость пикселя
    brightness = gray_array[yi, xi]
    
    # Тёмные участки = большая толщина
    darkness = 1.0 - (brightness / 255.0)
    thickness = min_thick + darkness * (max_thick - min_thick)
    
    return thickness


def draw_spiral_art(gray_array, spiral_points, output_path, 
                    min_thick=0.5, max_thick=6.0, scale=2):
    """
    Рисует спиральное изображение.
    """
    h, w = gray_array.shape
    
    # Создаём белое изображение
    img = Image.new('L', (int(w * scale), int(h * scale)), 255)
    draw = ImageDraw.Draw(img)
    
    # Рисуем сегменты спирали
    prev_point = None
    prev_thickness = None
    
    for i, (x, y) in enumerate(spiral_points):
        # Получаем толщину для текущей точки
        thickness = get_line_thickness(gray_array, x, y, min_thick, max_thick)
        
        if prev_point is not None:
            # Масштабируем координаты
            x1 = prev_point[0] * scale
            y1 = prev_point[1] * scale
            x2 = x * scale
            y2 = y * scale
            
            # Средняя толщина между двумя точками
            avg_thickness = (prev_thickness + thickness) / 2
            
            # Рисуем линию
            draw.line([(x1, y1), (x2, y2)], fill=0, width=max(1, int(avg_thickness)))
        
        prev_point = (x, y)
        prev_thickness = thickness
    
    # Сохраняем
    img.save(output_path, quality=95)
    print(f"Сохранено: {output_path}")


def generate_archimedean_spiral(width, height, num_turns=40, points_per_turn=100):
    """
    Генерирует архимедову спираль с равномерным шагом.
    """
    cx, cy = width / 2, height / 2
    
    # Максимальный радиус
    max_r = min(width, height) / 2 * 0.9
    
    points = []
    total_points = num_turns * points_per_turn
    
    for i in range(total_points):
        t = i / total_points
        
        # Угол
        angle = t * num_turns * 2 * math.pi
        
        # Радиус растёт линейно
        r = max_r * t
        
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        
        points.append((x, y))
    
    return points


def generate_random_walk(width, height, num_steps=2000, step_size=4.0,
                         start_from_center=True, bias_towards_center=True,
                         bias_strength=0.05, seed=None):
    """
    Генерирует путь случайного блуждания (random walk).
    
    Точка начинает путь из центра (или случайной позиции) и делает
    последовательные шаги в случайных направлениях. Притяжение к центру
    не даёт точке уйти за края изображения.
    
    Args:
        width: ширина изображения
        height: высота изображения
        num_steps: количество шагов
        step_size: длина одного шага в пикселях
        start_from_center: начинать из центра (иначе — случайная точка)
        bias_towards_center: притягивать точку к центру
        bias_strength: сила притяжения к центру (0.0 — нет, 1.0 — сильно)
        seed: seed для воспроизводимости (None = случайно)
    
    Returns:
        list of (x, y) — точки пути
    """
    import random
    
    if seed is not None:
        random.seed(seed)
    
    cx, cy = width / 2, height / 2
    
    if start_from_center:
        x, y = cx, cy
    else:
        x = random.uniform(0, width)
        y = random.uniform(0, height)
    
    points = [(x, y)]
    
    for _ in range(num_steps):
        # Случайное направление
        angle = random.uniform(0, 2 * math.pi)
        
        dx = math.cos(angle) * step_size
        dy = math.sin(angle) * step_size
        
        # Притяжение к центру
        if bias_towards_center:
            dx += (cx - x) * bias_strength
            dy += (cy - y) * bias_strength
        
        x += dx
        y += dy
        
        # Если вышли за границы — отражаем или телепортируем к центру
        if x < 0 or x >= width or y < 0 or y >= height:
            if bias_towards_center:
                # Телепортируем ближе к центру
                x = cx + random.uniform(-width * 0.2, width * 0.2)
                y = cy + random.uniform(-height * 0.2, height * 0.2)
            else:
                # Отражаем
                x = max(0, min(width - 1, x))
                y = max(0, min(height - 1, y))
        
        points.append((x, y))
    
    return points


def generate_rectangular_spiral(width, height, num_turns=40, points_per_turn=100):
    """
    Генерирует прямоугольную спираль от центра к краям.
    
    Спираль строится параметрически: угол меняется от 0 до num_turns*2*pi,
    а радиус — линейно от 0 до max_r. Форма приближается к прямоугольной
    через преобразование окружности в прямоугольник (sup-norm).
    
    width: ширина изображения
    height: высота изображения
    num_turns: количество витков
    points_per_turn: точек на один виток
    
    Возвращает список точек [(x1, y1), (x2, y2), ...]
    """
    cx, cy = width / 2, height / 2
    
    # Максимальный радиус по полуосям
    max_rx = width / 2 * 0.95
    max_ry = height / 2 * 0.95
    
    points = []
    total_points = num_turns * points_per_turn
    
    for i in range(total_points):
        t = i / total_points  # 0..1
        
        # Угол
        angle = t * num_turns * 2 * math.pi
        
        # Радиус растёт линейно
        r_progress = t  # 0..1
        
        # Преобразуем окружность в прямоугольник через sup-norm:
        #   x = r * cos(a), y = r * sin(a)
        #   чтобы получить квадрат, нормализуем: max(|cos|, |sin|)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        norm = max(abs(cos_a), abs(sin_a))
        
        if norm > 1e-10:
            # "Скругляем" прямоугольник, чтобы углы не были слишком острыми
            # Используем smooth-фактор: смешиваем окружность и прямоугольник
            smooth = 0.85  # 1.0 = чистый прямоугольник, 0.0 = окружность
            rect_cos = cos_a / norm
            rect_sin = sin_a / norm
            mix_cos = (1 - smooth) * cos_a + smooth * rect_cos
            mix_sin = (1 - smooth) * sin_a + smooth * rect_sin
        else:
            mix_cos = cos_a
            mix_sin = sin_a
        
        rx = max_rx * r_progress
        ry = max_ry * r_progress
        
        x = cx + rx * mix_cos
        y = cy + ry * mix_sin
        
        points.append((x, y))
    
    return points


def _point_in_convex_polygon(px, py, vertices):
    """
    Проверяет, находится ли точка (px, py) внутри выпуклого многоугольника.
    vertices — список вершин (x, y) в порядке обхода.
    """
    n = len(vertices)
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        # Векторное произведение: (P - V1) x (V2 - V1)
        cross = (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)
        if cross < 0:
            return False
    return True


def _clip_line_to_polygon(x1, y1, x2, y2, vertices):
    """
    Обрезает отрезок по выпуклому многоугольнику.
    Использует алгоритм Лян-Барски для выпуклых многоугольников.
    Возвращает (new_x1, new_y1, new_x2, new_y2) или None, если отрезок вне полигона.
    """
    dx = x2 - x1
    dy = y2 - y1
    
    t_min = 0.0
    t_max = 1.0
    
    n = len(vertices)
    for i in range(n):
        # Ребро полигона: от v1 к v2
        v1 = vertices[i]
        v2 = vertices[(i + 1) % n]
        
        # Внутренняя нормаль к ребру (перпендикуляр, направленный внутрь)
        # Для выпуклого многоугольника с обходом против часовой стрелки
        edge_x = v2[0] - v1[0]
        edge_y = v2[1] - v1[1]
        # Нормаль, направленная внутрь: (-edge_y, edge_x) для CCW
        nx = -edge_y
        ny = edge_x
        
        # Расстояние от точки на отрезке до ребра вдоль нормали
        # denominator = nx * dx + ny * dy
        denom = nx * dx + ny * dy
        # numerator = nx * (x1 - v1[0]) + ny * (y1 - v1[1])
        numer = nx * (x1 - v1[0]) + ny * (y1 - v1[1])
        
        if abs(denom) < 1e-10:
            # Отрезок параллелен ребру
            if numer < 0:
                return None  # Отрезок снаружи
            else:
                continue  # Отрезок внутри или на границе
        else:
            t = -numer / denom
            if denom > 0:
                # Входим в полигон
                t_min = max(t_min, t)
            else:
                # Выходим из полигона
                t_max = min(t_max, t)
            
            if t_min > t_max:
                return None
    
    if t_min > t_max:
        return None
    
    cx1 = x1 + t_min * dx
    cy1 = y1 + t_min * dy
    cx2 = x1 + t_max * dx
    cy2 = y1 + t_max * dy
    
    return (cx1, cy1, cx2, cy2)


def generate_hex_art(gray_array, output_path, hex_size=20,
                     min_step=2.0, max_step=20.0, angle=0.0,
                     line_width=1.0, scale=2, show_grid=False):
    """
    Генерирует изображение в сотовой структуре.
    
    Изображение разбивается на правильные шестиугольники (pointy-top).
    Внутри каждого шестиугольника рисуются параллельные линии (штриховка).
    Расстояние между линиями зависит от средней яркости пикселей внутри соты:
    темнее → линии чаще (меньше шаг), светлее → линии реже (больше шаг).
    
    Args:
        gray_array: np.ndarray — изображение в оттенках серого
        output_path: str — путь для сохранения
        hex_size: int — радиус шестиугольника в пикселях
        min_step: float — минимальный шаг штриховки (для тёмных участков)
        max_step: float — максимальный шаг штриховки (для светлых участков)
        angle: float — угол наклона штриховки в градусах
        line_width: float — толщина линии штриховки
        scale: int — масштаб выходного изображения
        show_grid: bool — рисовать контуры шестиугольников
    """
    import numpy as np
    from PIL import Image, ImageDraw
    import math
    
    h, w = gray_array.shape
    
    # Создаём выходное изображение (белый фон)
    img = Image.new('L', (int(w * scale), int(h * scale)), 255)
    draw = ImageDraw.Draw(img)
    
    # Параметры гексагональной решётки
    # Шестиугольник с "pointy-top" ориентацией (вершина сверху)
    R = hex_size  # радиус описанной окружности
    
    # Размеры шестиугольника
    hex_w = math.sqrt(3) * R  # ширина (по x)
    hex_h = 2 * R             # высота (по y)
    
    # Шаг сетки
    dx = hex_w                # расстояние между центрами по x
    dy = 1.5 * R              # расстояние между центрами по y
    x_offset = dx / 2         # смещение для чётных рядов
    
    # Угол штриховки в радианах
    angle_rad = math.radians(angle)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    
    # Вершины шестиугольника (pointy-top: первая вершина сверху)
    # Углы: 90°, 150°, 210°, 270°, 330°, 30°
    hex_vertices_local = []
    for i in range(6):
        a = math.radians(90 + 60 * i)
        hex_vertices_local.append((R * math.cos(a), R * math.sin(a)))
    
    # Проходим по всем сотам, покрывающим изображение
    for row in range(int(h / dy) + 3):
        for col in range(int(w / dx) + 3):
            # Центр соты
            cx = col * dx + (x_offset if row % 2 == 1 else 0)
            cy = row * dy + R  # смещение на R, чтобы верхняя вершина была на y=0
            
            # Проверяем, что сота хотя бы частично в пределах изображения
            if cx - R > w or cx + R < 0 or cy - R > h or cy + R < 0:
                continue
            
            # Вершины соты в абсолютных координатах
            hex_vertices_abs = [(cx + vx, cy + vy) for vx, vy in hex_vertices_local]
            
            # Вычисляем среднюю яркость пикселей внутри шестиугольника
            min_x = max(0, int(cx - R))
            max_x = min(w, int(cx + R) + 1)
            min_y = max(0, int(cy - R))
            max_y = min(h, int(cy + R) + 1)
            
            pixels = []
            for py in range(min_y, max_y):
                for px in range(min_x, max_x):
                    if _point_in_convex_polygon(px, py, hex_vertices_abs):
                        pixels.append(gray_array[py, px])
            
            if not pixels:
                continue
            
            avg_brightness = sum(pixels) / len(pixels)
            brightness_norm = avg_brightness / 255.0
            
            # Шаг штриховки: темнее → меньше шаг
            step = min_step + (1.0 - brightness_norm) * (max_step - min_step)
            
            # Рисуем штриховку внутри шестиугольника
            # Длина диагонали описанной окружности
            diag = 2 * R
            
            # Направление, перпендикулярное линиям штриховки
            perp_angle = angle_rad + math.pi / 2
            perp_cos = math.cos(perp_angle)
            perp_sin = math.sin(perp_angle)
            
            # Идём с шагом step вдоль перпендикулярного направления
            # Начинаем от центра и идём в обе стороны
            max_dist = diag  # максимальное расстояние от центра вдоль перпендикуляра
            
            dist = -max_dist
            while dist < max_dist:
                # Точка на линии, проходящей через центр соты,
                # смещённая на dist вдоль перпендикулярного направления
                mid_x = cx + dist * perp_cos
                mid_y = cy + dist * perp_sin
                
                # Концы отрезка вдоль направления штриховки
                x1 = mid_x - diag * cos_a
                y1 = mid_y - diag * sin_a
                x2 = mid_x + diag * cos_a
                y2 = mid_y + diag * sin_a
                
                # Обрезаем отрезок по границам шестиугольника
                clipped = _clip_line_to_polygon(x1, y1, x2, y2, hex_vertices_abs)
                if clipped is not None:
                    cx1, cy1, cx2, cy2 = clipped
                    # Масштабируем
                    sx1 = cx1 * scale
                    sy1 = cy1 * scale
                    sx2 = cx2 * scale
                    sy2 = cy2 * scale
                    draw.line([(sx1, sy1), (sx2, sy2)], fill=0, width=max(1, int(line_width)))
                
                dist += step
            
            # Рисуем контур шестиугольника, если нужно
            if show_grid:
                for i in range(6):
                    x1, y1 = hex_vertices_abs[i]
                    x2, y2 = hex_vertices_abs[(i + 1) % 6]
                    sx1 = x1 * scale
                    sy1 = y1 * scale
                    sx2 = x2 * scale
                    sy2 = y2 * scale
                    draw.line([(sx1, sy1), (sx2, sy2)], fill=0, width=max(1, int(line_width)))
    
    img.save(output_path, quality=95)
    print(f"Сохранено: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Spiral Line Art Generator — одна спираль переменной толщины"
    )
    parser.add_argument("input", help="Путь к исходному изображению")
    parser.add_argument("-o", "--output", default="spiral_art", 
                        help="Имя выходного файла")
    parser.add_argument("-W", "--width", type=int, default=800, 
                        help="Ширина в пикселях")
    parser.add_argument("--turns", type=int, default=40, 
                        help="Количество витков спирали")
    parser.add_argument("--min-thick", type=float, default=0.5, 
                        help="Минимальная толщина линии")
    parser.add_argument("--max-thick", type=float, default=6.0, 
                        help="Максимальная толщина линии")
    parser.add_argument("--scale", type=int, default=2, 
                        help="Масштаб вывода PNG")
    parser.add_argument("--type", choices=["archimedean", "elliptical", "rectangular"],
                        default="archimedean", help="Тип спирали")
    parser.add_argument("--step", type=int, default=10, 
                        help="Шаг для прямоугольной спирали (устаревший параметр)")
    
    args = parser.parse_args()
    
    print(f"Загрузка: {args.input}")
    gray = load_and_preprocess(args.input, args.width)
    h, w = gray.shape
    print(f"  Размер: {w}x{h}")
    
    # Генерируем путь спирали
    print(f"Генерация спирали типа '{args.type}'...")
    
    if args.type == "archimedean":
        spiral_points = generate_archimedean_spiral(w, h, args.turns)
    elif args.type == "elliptical":
        spiral_points = generate_spiral_path(w, h, args.turns)
    elif args.type == "rectangular":
        spiral_points = generate_rectangular_spiral(w, h, args.turns)
    
    print(f"  Точек в спирали: {len(spiral_points)}")
    
    # Рисуем изображение
    print("Отрисовка...")
    output_path = f"{args.output}.png"
    draw_spiral_art(
        gray, spiral_points, output_path,
        args.min_thick, args.max_thick, args.scale
    )
    
    print("Готово!")


if __name__ == "__main__":
    main()