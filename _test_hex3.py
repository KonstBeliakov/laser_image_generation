import sys, traceback
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from spiral_generator import load_and_preprocess, generate_hex_art, _point_in_convex_polygon, _clip_line_to_polygon
import math

# Тест point-in-polygon
# Шестиугольник flat-top с центром в (0,0), R=20
R = 20
vertices = []
for i in range(6):
    a = math.radians(60 * i)
    vertices.append((R * math.cos(a), R * math.sin(a)))

print("Vertices:", vertices)

# Точка в центре должна быть внутри
print("Center (0,0) inside:", _point_in_convex_polygon(0, 0, vertices))
# Точка далеко снаружи
print("Far (100,100) inside:", _point_in_convex_polygon(100, 100, vertices))
# Точка на границе
print("On edge (20,0) inside:", _point_in_convex_polygon(20, 0, vertices))

# Тест клиппинга
# Линия через центр
clipped = _clip_line_to_polygon(-30, 0, 30, 0, vertices)
print("Clip through center:", clipped)

# Теперь сдвинем шестиугольник в (50, 50)
cx, cy = 50, 50
abs_vertices = [(cx+vx, cy+vy) for vx, vy in vertices]
print("Abs vertices:", abs_vertices)
print("Center (50,50) inside:", _point_in_convex_polygon(50, 50, abs_vertices))

# Линия через центр (50,50)
clipped2 = _clip_line_to_polygon(20, 50, 80, 50, abs_vertices)
print("Clip through abs center:", clipped2)

# Тест generate_hex_art с маленьким изображением
from PIL import Image
import numpy as np

# Создаём маленькое чёрно-белое изображение
gray = np.zeros((100, 100), dtype=np.float32)
gray[30:70, 30:70] = 128  # серый квадрат

generate_hex_art(gray, 'test_hex3.png', hex_size=15, min_step=2, max_step=15, angle=0, line_width=1, scale=2)
print('test_hex3 done')
