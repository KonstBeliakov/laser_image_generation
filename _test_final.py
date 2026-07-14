import sys, traceback
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from spiral_generator import load_and_preprocess, generate_hex_art

try:
    gray = load_and_preprocess('miku.jpg', 200)
    print('Shape:', gray.shape)
    generate_hex_art(gray, 'test_hex_final.png', hex_size=20, min_step=2, max_step=20, angle=0, line_width=1, scale=2)
    import os
    print('Size:', os.path.getsize('test_hex_final.png'))
except Exception as e:
    traceback.print_exc()
