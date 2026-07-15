import sys, traceback
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from spiral_generator import _build_snake_cycle, _build_random_hamiltonian_cycle

# Тест с маленькой сеткой 4x3 (12 узлов)
cols, rows = 4, 3
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

# Строим случайный
random.seed(123)
ham = _build_random_hamiltonian_cycle(cols, rows, seed=123)
print(f"\nHamiltonian ({len(ham)}): {ham}")

# Проверяем рёбра
print("Рёбра hamiltonian:")
bad = 0
for i in range(len(ham)):
    a = ham[i]
    b = ham[(i + 1) % len(ham)]
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    ok = "OK" if dx + dy == 1 else "BAD"
    if ok == "BAD":
        bad += 1
    print(f"  {a} -> {b}  ({ok})")

print(f"\nПлохих рёбер: {bad} / {len(ham)}")
print(f"Отличается от snake: {ham != snake}")
