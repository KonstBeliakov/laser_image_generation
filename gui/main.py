"""
Точка входа для GUI Spiral Line Art Generator.
Запуск: python -m gui.main
"""

import sys
import os

# Добавляем корневую папку проекта в sys.path, чтобы импорт spiral_generator работал
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from gui.app import MainApp


def main():
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
