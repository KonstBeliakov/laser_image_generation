import sys, traceback
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from spiral_generator import load_and_preprocess, _point_in_convex_polygon, _clip_line_to_polygon
import math
from PIL import Image, ImageDraw
import numpy as np

gray = load_and_preprocess('miku.jpg', 200)
h, w = gray.shape
print(f'Image: {w}x{h}')

scale = 2
img = Image.new('L', (int(w * scale), int(h * scale)), 255)
draw = ImageDraw.Draw(img)

R = 20
r = R * math.sqrt(3) / 2

hex_vertices_local = []
for i in range(6):
    a = math.radians(60 * i)
    hex_vertices_local.append((R * math.cos(a), R * math.sin(a)))

dx = 1.5 * R
dy = math.sqrt(3) * R
x_offset = dx / 2

total_lines = 0
total_cells = 0
cells_with_lines = 0

for row in range(int(h / dy) + 3):
    for col in range(int(w / dx) + 3):
        cx = col * dx + (x_offset if row % 2 == 1 else 0)
        cy = row * dy + r
        
        if cx - R > w or cx + R < 0 or cy - R > h or cy + R < 0:
            continue
        
        hex_vertices_abs = [(cx + vx, cy + vy) for vx, vy in hex_vertices_local]
        
        min_x = max(0, int(cx - R))
        max_x = min(w, int(cx + R) + 1)
        min_y = max(0, int(cy - R))
        max_y = min(h, int(cy + R) + 1)
        
        pixels = []
        for py in range(min_y, max_y):
            for px in range(min_x, max_x):
                if _point_in_convex_polygon(px, py, hex_vertices_abs):
                    pixels.append(gray[py, px])
        
        if not pixels:
            continue
        
        total_cells += 1
        avg_brightness = sum(pixels) / len(pixels)
        brightness_norm = avg_brightness / 255.0
        
        min_step = 2.0
        max_step = 20.0
        step = min_step + (1.0 - brightness_norm) * (max_step - min_step)
        
        diag = 2 * R
        angle_rad = 0.0
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        perp_angle = angle_rad + math.pi / 2
        perp_cos = math.cos(perp_angle)
        perp_sin = math.sin(perp_angle)
        
        max_dist = diag
        dist = -max_dist
        lines_in_cell = 0
        
        while dist < max_dist:
            mid_x = cx + dist * perp_cos
            mid_y = cy + dist * perp_sin
            
            x1 = mid_x - diag * cos_a
            y1 = mid_y - diag * sin_a
            x2 = mid_x + diag * cos_a
            y2 = mid_y + diag * sin_a
            
            clipped = _clip_line_to_polygon(x1, y1, x2, y2, hex_vertices_abs)
            if clipped is not None:
                cx1, cy1, cx2, cy2 = clipped
                sx1 = cx1 * scale
                sy1 = cy1 * scale
                sx2 = cx2 * scale
                sy2 = cy2 * scale
                draw.line([(sx1, sy1), (sx2, sy2)], fill=0, width=1)
                lines_in_cell += 1
                total_lines += 1
            
            dist += step
        
        if lines_in_cell > 0:
            cells_with_lines += 1

print(f'Total cells: {total_cells}, cells with lines: {cells_with_lines}, total lines: {total_lines}')
img.save('test_debug.png', quality=95)
print('Saved test_debug.png')
import os
print('Size:', os.path.getsize('test_debug.png'))
