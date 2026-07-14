import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from spiral_generator import _point_in_convex_polygon, _clip_line_to_polygon
import math

R = 15
# Flat-top: углы 0, 60, 120, 180, 240, 300
vertices = []
for i in range(6):
    a = math.radians(60 * i)
    vertices.append((R * math.cos(a), R * math.sin(a)))

print("Vertices (flat-top):")
for i, (x, y) in enumerate(vertices):
    print(f"  {i}: ({x:.1f}, {y:.1f})")

# Проверяем порядок обхода: вычисляем площадь (знак = направление)
area = 0
n = len(vertices)
for i in range(n):
    x1, y1 = vertices[i]
    x2, y2 = vertices[(i + 1) % n]
    area += x1 * y2 - x2 * y1
area /= 2
print(f"Signed area: {area:.1f} (positive = CCW, negative = CW)")

# Тест: линия через центр (0,0) должна обрезаться
clipped = _clip_line_to_polygon(-30, 0, 30, 0, vertices)
print(f"Clip (-30,0)-(30,0) through center: {clipped}")

# Тест: линия, смещённая от центра
clipped2 = _clip_line_to_polygon(-30, 5, 30, 5, vertices)
print(f"Clip (-30,5)-(30,5) offset: {clipped2}")

# Тест: линия далеко снаружи
clipped3 = _clip_line_to_polygon(-30, 30, 30, 30, vertices)
print(f"Clip (-30,30)-(30,30) outside: {clipped3}")

# Тест: много линий с шагом 2
cx, cy = 0, 0
hex_abs = vertices  # центр в (0,0)
diag = 2 * R
angle_rad = 0.0
cos_a = math.cos(angle_rad)
sin_a = math.sin(angle_rad)
perp_angle = angle_rad + math.pi / 2
perp_cos = math.cos(perp_angle)
perp_sin = math.sin(perp_angle)

count = 0
dist = -diag
step = 2.0
while dist < diag:
    mid_x = cx + dist * perp_cos
    mid_y = cy + dist * perp_sin
    x1 = mid_x - diag * cos_a
    y1 = mid_y - diag * sin_a
    x2 = mid_x + diag * cos_a
    y2 = mid_y + diag * sin_a
    clipped = _clip_line_to_polygon(x1, y1, x2, y2, hex_abs)
    if clipped is not None:
        count += 1
    dist += step

print(f"\nLines with step=2: {count} clipped out of {int(2*diag/step)} total")
