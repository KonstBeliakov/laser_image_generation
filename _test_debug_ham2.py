import sys, traceback, random
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from spiral_generator import _build_snake_cycle, _build_random_hamiltonian_cycle, _reverse_segment

# Тест с сеткой 6x4 (24 узла, rows чётное)
cols, rows = 6, 4
print(f"Сетка {cols}x{rows}")

# Смотрим snake cycle
snake = _build_snake_cycle(cols, rows)
print(f"Snake ({len(snake)}): {snake}")

# Проверяем рёбра snake
print("Рёбра snake:")
for i in range(len(snake)):
    a = snake[i]
    b = snake[(i + 1) % len(snake)]
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    ok = "OK" if dx + dy == 1 else "BAD"
    print(f"  {a} -> {b}  ({ok})")

# Ручной тест flip
print("\n--- Ручной тест flip ---")
cycle = list(snake)
n = len(cycle)

# Выбираем curr = (0,0) (индекс 0), nxt = (1,0) (индекс 1)
# Соседи curr по сетке: (1,0)=nxt, (-1,0)=нет, (0,1)=C, (0,-1)=нет
# target = (0,1) — это C
# Находим C в цикле: (0,1) на индексе 7
# prev_target = 6 = (1,1)
# Проверяем: cycle[6]=(1,1) != curr=(0,0) — OK
# Порядок: curr -> nxt -> ... -> prev_target -> target
# nxt=(1,0) на индексе 1, target=(0,1) на индексе 7
# Идём от curr: (1,0), (2,0), (3,0), (3,1), (2,1), (1,1), (0,1)
# found_nxt на 1, found_target на 7
# found_nxt && !found_target — нет, found_target && !found_nxt — нет
# Оба найдены! Ни одно условие не сработало!

# Проблема: found_nxt и found_target оба True, потому что оба узла
# находятся в цикле после curr. Нужно проверять, кто встретится ПЕРВЫМ.

print("\nАнализ:")
idx = 0  # curr = (0,0)
next_idx = 1  # nxt = (1,0)
curr = cycle[idx]  # (0,0)
nxt = cycle[next_idx]  # (1,0)
target = (0, 1)  # C
i_target = 7
prev_target = 6

print(f"curr={curr}, nxt={nxt}, target={target}")
print(f"idx={idx}, next_idx={next_idx}, i_target={i_target}, prev_target={prev_target}")

# Идём от curr вперёд и смотрим, кто встретится ПЕРВЫМ
i = next_idx
first_found = None
while True:
    if cycle[i] == nxt and first_found is None:
        first_found = 'nxt'
    if cycle[i] == target and first_found is None:
        first_found = 'target'
    i = (i + 1) % n
    if i == idx:
        break

print(f"Первый встретился: {first_found}")
print(f"nxt на {next_idx}, target на {i_target}")

# Проблема: nxt и target могут быть в разных порядках.
# Нужно проверять, кто ПЕРВЫЙ встретится после curr.
