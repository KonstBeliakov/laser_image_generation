"""
Вкладка "Спираль" — генерация изображения одной непрерывной спиралью.
"""

import tkinter as tk
from tkinter import ttk

from gui.tabs.base_tab import BaseTab
from spiral_generator import (
    generate_spiral_path,
    generate_archimedean_spiral,
    generate_rectangular_spiral,
    draw_spiral_art,
)


class SpiralTab(BaseTab):
    def __init__(self, parent):
        self.spiral_type = tk.StringVar(value="archimedean")
        self.width_var = tk.IntVar(value=800)
        self.turns_var = tk.IntVar(value=40)
        self.scale_var = tk.IntVar(value=2)
        self.min_thick_var = tk.DoubleVar(value=0.5)
        self.max_thick_var = tk.DoubleVar(value=6.0)
        super().__init__(parent)

    def _build_ui(self):
        # Тип спирали
        ttk.Label(self, text="Тип спирали:").grid(
            row=0, column=0, sticky="w", padx=(0, 5), pady=3
        )
        type_combo = ttk.Combobox(
            self,
            textvariable=self.spiral_type,
            values=["archimedean", "elliptical", "rectangular"],
            state="readonly",
            width=20,
        )
        type_combo.grid(row=0, column=1, sticky="w", padx=5, pady=3)

        # Ширина
        ttk.Label(self, text="Ширина (px):").grid(
            row=1, column=0, sticky="w", padx=(0, 5), pady=3
        )
        ttk.Spinbox(
            self, from_=100, to=4000, textvariable=self.width_var, width=10
        ).grid(row=1, column=1, sticky="w", padx=5, pady=3)

        # Витки
        ttk.Label(self, text="Витки:").grid(
            row=2, column=0, sticky="w", padx=(0, 5), pady=3
        )
        ttk.Spinbox(
            self, from_=5, to=500, textvariable=self.turns_var, width=10
        ).grid(row=2, column=1, sticky="w", padx=5, pady=3)

        # Масштаб
        ttk.Label(self, text="Масштаб:").grid(
            row=3, column=0, sticky="w", padx=(0, 5), pady=3
        )
        ttk.Spinbox(
            self, from_=1, to=10, textvariable=self.scale_var, width=10
        ).grid(row=3, column=1, sticky="w", padx=5, pady=3)

        # Мин. толщина
        ttk.Label(self, text="Мин. толщина:").grid(
            row=4, column=0, sticky="w", padx=(0, 5), pady=3
        )
        ttk.Spinbox(
            self, from_=0.1, to=20.0, increment=0.1,
            textvariable=self.min_thick_var, width=10
        ).grid(row=4, column=1, sticky="w", padx=5, pady=3)

        # Макс. толщина
        ttk.Label(self, text="Макс. толщина:").grid(
            row=5, column=0, sticky="w", padx=(0, 5), pady=3
        )
        ttk.Spinbox(
            self, from_=0.1, to=20.0, increment=0.1,
            textvariable=self.max_thick_var, width=10
        ).grid(row=5, column=1, sticky="w", padx=5, pady=3)

    def generate(self, gray_array, output_path, status_callback):
        h, w = gray_array.shape
        spiral_type = self.spiral_type.get()
        turns = self.turns_var.get()
        scale = self.scale_var.get()
        min_thick = self.min_thick_var.get()
        max_thick = self.max_thick_var.get()

        status_callback(f"Генерация спирали ({spiral_type})...")
        if spiral_type == "archimedean":
            spiral_points = generate_archimedean_spiral(w, h, turns)
        elif spiral_type == "elliptical":
            spiral_points = generate_spiral_path(w, h, turns)
        elif spiral_type == "rectangular":
            spiral_points = generate_rectangular_spiral(w, h, turns)
        else:
            raise ValueError(f"Неизвестный тип спирали: {spiral_type}")

        status_callback("Отрисовка...")
        draw_spiral_art(gray_array, spiral_points, output_path,
                        min_thick, max_thick, scale)

        return output_path
