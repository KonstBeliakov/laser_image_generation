"""
Вкладка "Соты" — изображение разбивается на шестиугольники,
каждый из которых заштриховывается линиями с переменным шагом.
"""

import tkinter as tk
from tkinter import ttk

from gui.tabs.base_tab import BaseTab
from spiral_generator import generate_hex_art


class HexTab(BaseTab):
    def __init__(self, parent):
        self.hex_size_var = tk.IntVar(value=20)
        self.min_step_var = tk.DoubleVar(value=2.0)
        self.max_step_var = tk.DoubleVar(value=20.0)
        self.angle_var = tk.DoubleVar(value=0.0)
        self.line_width_var = tk.DoubleVar(value=1.0)
        self.scale_var = tk.IntVar(value=2)
        self.show_grid_var = tk.BooleanVar(value=False)
        super().__init__(parent)

    def _build_ui(self):
        # Размер шестиугольника
        ttk.Label(self, text="Размер соты (px):").grid(
            row=0, column=0, sticky="w", padx=(0, 5), pady=3
        )
        ttk.Spinbox(
            self, from_=5, to=100, textvariable=self.hex_size_var, width=10
        ).grid(row=0, column=1, sticky="w", padx=5, pady=3)

        # Мин. шаг штриховки
        ttk.Label(self, text="Мин. шаг штриховки:").grid(
            row=1, column=0, sticky="w", padx=(0, 5), pady=3
        )
        ttk.Spinbox(
            self, from_=0.5, to=50.0, increment=0.5,
            textvariable=self.min_step_var, width=10
        ).grid(row=1, column=1, sticky="w", padx=5, pady=3)

        # Макс. шаг штриховки
        ttk.Label(self, text="Макс. шаг штриховки:").grid(
            row=2, column=0, sticky="w", padx=(0, 5), pady=3
        )
        ttk.Spinbox(
            self, from_=0.5, to=50.0, increment=0.5,
            textvariable=self.max_step_var, width=10
        ).grid(row=2, column=1, sticky="w", padx=5, pady=3)

        # Угол наклона штриховки
        ttk.Label(self, text="Угол штриховки (°):").grid(
            row=3, column=0, sticky="w", padx=(0, 5), pady=3
        )
        ttk.Spinbox(
            self, from_=0, to=180, increment=5,
            textvariable=self.angle_var, width=10
        ).grid(row=3, column=1, sticky="w", padx=5, pady=3)

        # Толщина линии
        ttk.Label(self, text="Толщина линии:").grid(
            row=4, column=0, sticky="w", padx=(0, 5), pady=3
        )
        ttk.Spinbox(
            self, from_=0.5, to=10.0, increment=0.5,
            textvariable=self.line_width_var, width=10
        ).grid(row=4, column=1, sticky="w", padx=5, pady=3)

        # Масштаб
        ttk.Label(self, text="Масштаб:").grid(
            row=5, column=0, sticky="w", padx=(0, 5), pady=3
        )
        ttk.Spinbox(
            self, from_=1, to=10, textvariable=self.scale_var, width=10
        ).grid(row=5, column=1, sticky="w", padx=5, pady=3)

        # Показывать сетку
        ttk.Checkbutton(
            self, text="Показывать сетку шестиугольников",
            variable=self.show_grid_var
        ).grid(row=6, column=0, columnspan=2, sticky="w", padx=5, pady=3)

    def generate(self, gray_array, output_path, status_callback):
        hex_size = self.hex_size_var.get()
        min_step = self.min_step_var.get()
        max_step = self.max_step_var.get()
        angle = self.angle_var.get()
        line_width = self.line_width_var.get()
        scale = self.scale_var.get()
        show_grid = self.show_grid_var.get()

        status_callback("Генерация сотовой структуры...")
        generate_hex_art(
            gray_array, output_path,
            hex_size=hex_size,
            min_step=min_step,
            max_step=max_step,
            angle=angle,
            line_width=line_width,
            scale=scale,
            show_grid=show_grid,
        )

        return output_path
