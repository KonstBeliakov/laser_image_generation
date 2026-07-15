import sys, traceback
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from spiral_generator import generate_hamiltonian_cycle, draw_spiral_art, load_and_preprocess

try:
    gray = load_and_preprocess('miku.jpg', 800)
    print('Shape:', gray.shape)
    
    # Тест с сеткой 40px
    points = generate_hamiltonian_cycle(gray.shape[1], gray.shape[0], grid_size=40, shuffle_iterations=5000, seed=42)
    print('Points:', len(points))
    print('First 10:', points[:10])
    
    # Проверяем, что все рёбра — между соседними узлами
    # (расстояние по сетке должно быть step_x или step_y)
    step_x = 800 / (800/40 - 1) if 800/40 > 1 else 800
    step_y = 337 / (337/40 - 1) if 337/40 > 1 else 337
    print(f'step_x={step_x:.2f}, step_y={step_y:.2f}')
    
    bad_edges = 0
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i+1]
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        # Допускаем погрешность 1px
        if not (abs(dx - step_x) < 1 and dy < 1) and not (abs(dy - step_y) < 1 and dx < 1):
            bad_edges += 1
            if bad_edges <= 5:
                print(f'  Bad edge {i}: ({x1:.1f},{y1:.1f}) -> ({x2:.1f},{y2:.1f}), dx={dx:.1f}, dy={dy:.1f}')
    
    print(f'Bad edges: {bad_edges} / {len(points)-1}')
    
    draw_spiral_art(gray, points, 'test_hamiltonian2.png', min_thick=0.5, max_thick=5.0, scale=2)
    import os
    print('Size:', os.path.getsize('test_hamiltonian2.png'))
except Exception as e:
    traceback.print_exc()
