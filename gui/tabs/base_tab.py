"""
Базовый класс для вкладок генерации изображений.
"""

import tkinter as tk
from tkinter import ttk


class BaseTab(ttk.Frame):
    """
    Базовый класс для вкладки стиля генерации.
    
    Каждая вкладка должна:
    - Создать свои виджеты параметров в __init__
    - Реализовать метод generate(gray_array, output_path, status_callback)
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        """Создаёт виджеты параметров. Переопределяется в наследниках."""
        pass

    def generate(self, gray_array, output_path, status_callback):
        """
        Генерирует изображение.
        
        Args:
            gray_array: np.ndarray — изображение в оттенках серого
            output_path: str — путь для сохранения результата
            status_callback: callable(str) — функция для обновления статуса
        
        Returns:
            str — путь к сохранённому файлу
        """
        raise NotImplementedError("Наследник должен реализовать generate()")
