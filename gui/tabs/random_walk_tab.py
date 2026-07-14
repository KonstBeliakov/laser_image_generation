"""
Вкладка "Random Walk" — изображение рисуется случайным блужданием
с переменной толщиной линии в зависимости от яркости.
"""

import tkinter as tk
from tkinter import ttk

from gui.tabs.base_tab import BaseTab
from spiral_generator import (
    generate_random_walk,
    draw_spiral_art,
)


class RandomWalkTab(BaseTab):
    def __init__(self, parent):
        self.num_steps_var = tk.IntVar(value=2000)
        self.step_size_var = tk.DoubleVar(value=4.0)
        self.min_thick_var = tk.DoubleVar(value=0.5)
        self.max_thick_var = tk.DoubleVar(value=5.0)
        self.scale_var = tk.IntVar(value=2)
        self.start_from_center_var = tk.BooleanVar(value=True)
        self.bias_towards_center_var = tk.BooleanVar(value=True)
        self.bias_strength_var = tk.DoubleVar(value=0.05)
        self.seed_var = tk.StringVar(value="")
        super().__init__(parent)

    def _build_ui(self):
        # Количество шагов
        ttk.Label(self, text="Количество шагов:").grid(
            row=0, column=0, sticky="w", padx=(0, 5), pady=3
        )
        ttk.Spinbox(
            self, from_=100, to=50000, increment=100,
            textvariable=self.num_steps_var, width=10
        ).grid(row=0, column=1, sticky="w", padx=5, pady=3)

        # Длина шага
        ttk.Label(self, text="Длина шага (px):").grid(
            row=1, column=0, sticky="w", padx=(0, 5), pady=3
        )
        ttk.Spinbox(
            self, from_=0.5, to=20.0, increment=0.5,
            textvariable=self.step_size_var, width=10
        ).grid(row=1, column=1, sticky="w", padx=5, pady=3)

        # Мин. толщина
        ttk.Label(self, text="Мин. толщина:").grid(
            row=2, column=0, sticky="w", padx=(0, 5), pady=3
        )
        ttk.Spinbox(
            self, from_=0.1, to=20.0, increment=0.1,
            textvariable=self.min_thick_var, width=10
        ).grid(row=2, column=1, sticky="w", padx=5, pady=3)

        # Макс. толщина
        ttk.Label(self, text="Макс. толщина:").grid(
            row=3, column=0, sticky="w", padx=(0, 5), pady=3
        )
        ttk.Spinbox(
            self, from_=0.1, to=20.0, increment=0.1,
            textvariable=self.max_thick_var, width=10
        ).grid(row=3, column=1, sticky="w", padx=5, pady=3)

        # Масштаб
        ttk.Label(self, text="Масштаб:").grid(
            row=4, column=0, sticky="w", padx=(0, 5), pady=3
        )
        ttk.Spinbox(
            self, from_=1, to=10, textvariable=self.scale_var, width=10
        ).grid(row=4, column=1, sticky="w", padx=5, pady=3)

        # Начинать из центра
        ttk.Checkbutton(
            self, text="Начинать из центра",
            variable=self.start_from_center_var
        ).grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=3)

        # Притяжение к центру
        ttk.Checkbutton(
            self, text="Притяжение к центру",
            variable=self.bias_towards_center_var
        ).grid(row=6, column=0, columnspan=2, sticky="w", padx=5, pady=3)

        # Сила притяжения
        ttk.Label(self, text="Сила притяжения:").grid(
            row=7, column=0, sticky="w", padx=(0, 5), pady=3
        )
        ttk.Spinbox(
            self, from_=0.01, to=0.5, increment=0.01,
            textvariable=self.bias_strength_var, width=10
        ).grid(row=7, column=1, sticky="w", padx=5, pady=3)

        # Seed
        ttk.Label(self, text="Seed (оставьте пустым для случайного):").grid(
            row=8, column=0, sticky="w", padx=(0, 5), pady=3
        )
        ttk.Entry(
            self, textvariable=self.seed_var, width=12
        ).grid(row=8, column=1, sticky="w", padx=5, pady=3)

    def generate(self, gray_array, output_path, status_callback):
        h, w = gray_array.shape
        num_steps = self.num_steps_var.get()
        step_size = self.step_size_var.get()
        min_thick = self.min_thick_var.get()
        max_thick = self.max_thick_var.get()
        scale = self.scale_var.get()
        start_from_center = self.start_from_center_var.get()
        bias_towards_center = self.bias_towards_center_var.get()
        bias_strength = self.bias_strength_var.get()
        seed_str = self.seed_var.get().strip()
        seed = int(seed_str) if seed_str else None

        status_callback(f"Генерация random walk ({num_steps} шагов)...")
        points = generate_random_walk(
            w, h,
            num_steps=num_steps,
            step_size=step_size,
            start_from_center=start_from_center,
            bias_towards_center=bias_towards_center,
            bias_strength=bias_strength,
            seed=seed,
        )

        status_callback("Отрисовка...")
        draw_spiral_art(gray_array, points, output_path,
                        min_thick, max_thick, scale)

        return output_path
