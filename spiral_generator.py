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