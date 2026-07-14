import sys, traceback
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from spiral_generator import load_and_preprocess, generate_hex_art

try:
    gray = load_and_preprocess('miku.jpg', 800)
    print('Shape:', gray.shape)
    # Пробуем с большей толщиной линии
    generate_hex_art(gray, 'test_hex_thick.png', hex_size=20, min_step=2, max_step=20, angle=0, line_width=3, scale=2)
    import os
    print('Size thick:', os.path.getsize('test_hex_thick.png'))
    
    # Пробуем с меньшим шагом (больше линий)
    generate_hex_art(gray, 'test_hex_dense.png', hex_size=20, min_step=1, max_step=10, angle=0, line_width=1, scale=2)
    print('Size dense:', os.path.getsize('test_hex_dense.png'))
    
    # Пробуем с углом 45°
    generate_hex_art(gray, 'test_hex_angle.png', hex_size=20, min_step=2, max_step=20, angle=45, line_width=1, scale=2)
    print('Size angle:', os.path.getsize('test_hex_angle.png'))
except Exception as e:
    traceback.print_exc()
