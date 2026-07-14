import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import math
from PIL import Image, ImageDraw

# Тест покрытия плоскости pointy-top шестиугольниками
W, H = 400, 300
R = 30

# Pointy-top
hex_w = math.sqrt(3) * R
hex_h = 2 * R
dx = hex_w
dy = 1.5 * R
x_offset = dx / 2

print(f"R={R}, hex_w={hex_w:.1f}, hex_h={hex_h:.1f}")
print(f"dx={dx:.1f}, dy={dy:.1f}, x_offset={x_offset:.1f}")

# Вершины pointy-top
hex_local = []
for i in range(6):
    a = math.radians(90 + 60 * i)
    hex_local.append((R * math.cos(a), R * math.sin(a)))

img = Image.new('RGB', (W, H), 'white')
draw = ImageDraw.Draw(img)

# Рисуем сетку
for row in range(int(H / dy) + 3):
    for col in range(int(W / dx) + 3):
        cx = col * dx + (x_offset if row % 2 == 1 else 0)
        cy = row * dy + R
        
        verts = [(cx + vx, cy + vy) for vx, vy in hex_local]
        
        # Контур
        for i in range(6):
            x1, y1 = verts[i]
            x2, y2 = verts[(i + 1) % 6]
            draw.line([(x1, y1), (x2, y2)], fill='black', width=1)
        
        # Центр
        draw.point((cx, cy), fill='red')

# Закрасим фон, чтобы увидеть пробелы
# Каждый пиксель, не попавший ни в один шестиугольник, будет синим
# (упрощённо: просто проверим несколько точек)
for y in range(0, H, 5):
    for x in range(0, W, 5):
        inside_any = False
        for row in range(int(H / dy) + 3):
            for col in range(int(W / dx) + 3):
                cx = col * dx + (x_offset if row % 2 == 1 else 0)
                cy = row * dy + R
                verts = [(cx + vx, cy + vy) for vx, vy in hex_local]
                # Point-in-polygon
                inside = True
                n = len(verts)
                for i in range(n):
                    x1, y1 = verts[i]
                    x2, y2 = verts[(i + 1) % n]
                    cross = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)
                    if cross < 0:
                        inside = False
                        break
                if inside:
                    inside_any = True
                    break
            if inside_any:
                break
        if not inside_any:
            draw.point((x, y), fill='blue')

img.save('test_grid2.png')
print("Saved test_grid2.png")
