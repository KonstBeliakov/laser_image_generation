import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import math
from PIL import Image, ImageDraw

# Тест покрытия плоскости шестиугольниками
W, H = 400, 300
R = 30

# Pointy-top (вершина сверху)
# Ширина = sqrt(3) * R, высота = 2 * R
# Шаг по x = sqrt(3) * R, шаг по y = 1.5 * R
# Смещение чётных столбцов = 0.75 * R

hex_w = math.sqrt(3) * R  # ширина
hex_h = 2 * R             # высота
dx = hex_w                # шаг по x
dy = 1.5 * R              # шаг по y
x_offset = dx / 2         # смещение для чётных рядов

print(f"R={R}, hex_w={hex_w:.1f}, hex_h={hex_h:.1f}")
print(f"dx={dx:.1f}, dy={dy:.1f}, x_offset={x_offset:.1f}")

# Вершины pointy-top: первая вершина сверху (90°), затем через 60°
hex_local = []
for i in range(6):
    a = math.radians(90 + 60 * i)  # 90°, 150°, 210°, 270°, 330°, 30°
    hex_local.append((R * math.cos(a), R * math.sin(a)))

print("Pointy-top vertices:", [(f"{x:.1f}", f"{y:.1f}") for x, y in hex_local])

img = Image.new('RGB', (W, H), 'white')
draw = ImageDraw.Draw(img)

# Рисуем сетку
for row in range(int(H / dy) + 3):
    for col in range(int(W / dx) + 3):
        cx = col * dx + (x_offset if row % 2 == 1 else 0)
        cy = row * dy + R  # смещение на R, чтобы первая сота не обрезалась
        
        # Вершины в абсолютных координатах
        verts = [(cx + vx, cy + vy) for vx, vy in hex_local]
        
        # Рисуем контур
        for i in range(6):
            x1, y1 = verts[i]
            x2, y2 = verts[(i + 1) % 6]
            draw.line([(x1, y1), (x2, y2)], fill='black', width=1)
        
        # Центр
        draw.point((cx, cy), fill='red')

img.save('test_grid.png')
print("Saved test_grid.png")
