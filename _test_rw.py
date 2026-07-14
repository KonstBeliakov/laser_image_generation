import sys, traceback
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from spiral_generator import generate_random_walk, draw_spiral_art, load_and_preprocess

try:
    gray = load_and_preprocess('miku.jpg', 800)
    print('Shape:', gray.shape)
    points = generate_random_walk(gray.shape[1], gray.shape[0], num_steps=500, step_size=4.0)
    print('Points:', len(points))
    draw_spiral_art(gray, points, 'test_random_walk.png', min_thick=0.5, max_thick=5.0, scale=2)
    import os
    print('Size:', os.path.getsize('test_random_walk.png'))
except Exception as e:
    traceback.print_exc()
