import sys, traceback
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from spiral_generator import generate_hamiltonian_cycle, draw_spiral_art, load_and_preprocess

try:
    gray = load_and_preprocess('miku.jpg', 800)
    print('Shape:', gray.shape)
    
    # Тест с сеткой 40px
    points = generate_hamiltonian_cycle(gray.shape[1], gray.shape[0], grid_size=40, shuffle_iterations=2000, seed=42)
    print('Points:', len(points))
    print('First 5:', points[:5])
    
    draw_spiral_art(gray, points, 'test_hamiltonian.png', min_thick=0.5, max_thick=5.0, scale=2)
    import os
    print('Size:', os.path.getsize('test_hamiltonian.png'))
except Exception as e:
    traceback.print_exc()
