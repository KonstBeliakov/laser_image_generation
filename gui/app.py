"""
Spiral Line Art Generator — графическая оболочка на tkinter.
Многостилевой генератор с вкладками.
"""

import sys
import os

# Добавляем корневую папку проекта в sys.path, чтобы импорт spiral_generator работал
# при запуске как python gui/app.py, так и python -m gui.main
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

from PIL import Image, ImageTk

from spiral_generator import load_and_preprocess
from gui.tabs.spiral_tab import SpiralTab
from gui.tabs.hex_tab import HexTab
from gui.tabs.random_walk_tab import RandomWalkTab


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Line Art Generator")
        self.root.geometry("950x750")
        self.root.minsize(850, 650)

        # Общие переменные
        self.input_image_path = tk.StringVar()
        self.output_name = tk.StringVar(value="output")
        self.preview_input_tk = None
        self.preview_output_tk = None

        # Текущая активная вкладка
        self.current_tab = None

        self._build_ui()

    def _build_ui(self):
        # ---- Верхняя панель (общие параметры) ----
        top_frame = ttk.LabelFrame(self.root, text="Общие параметры", padding=10)
        top_frame.pack(fill="x", padx=10, pady=(10, 5))

        # Входной файл
        ttk.Label(top_frame, text="Входное изображение:").grid(
            row=0, column=0, sticky="w", padx=(0, 5), pady=3
        )
        self.input_entry = ttk.Entry(
            top_frame, textvariable=self.input_image_path, width=50
        )
        self.input_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=3)
        ttk.Button(
            top_frame, text="Обзор...", command=self._browse_input
        ).grid(row=0, column=2, padx=(5, 0), pady=3)

        # Выходной файл
        ttk.Label(top_frame, text="Выходной файл:").grid(
            row=1, column=0, sticky="w", padx=(0, 5), pady=3
        )
        ttk.Entry(
            top_frame, textvariable=self.output_name, width=50
        ).grid(row=1, column=1, sticky="ew", padx=5, pady=3)
        ttk.Label(top_frame, text="(без расширения)").grid(
            row=1, column=2, sticky="w", padx=(5, 0), pady=3
        )

        top_frame.columnconfigure(1, weight=1)

        # ---- Notebook (вкладки) ----
        notebook_frame = ttk.LabelFrame(self.root, text="Стиль генерации", padding=5)
        notebook_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill="x", expand=False)

        # Создаём вкладки
        self.tabs = {}
        self.tabs["spiral"] = SpiralTab(self.notebook)
        self.tabs["hex"] = HexTab(self.notebook)
        self.tabs["random_walk"] = RandomWalkTab(self.notebook)

        self.notebook.add(self.tabs["spiral"], text="Спираль")
        self.notebook.add(self.tabs["hex"], text="Соты")
        self.notebook.add(self.tabs["random_walk"], text="Random Walk")

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)
        self.current_tab = self.tabs["spiral"]

        # ---- Кнопка генерации ----
        btn_frame = ttk.Frame(notebook_frame)
        btn_frame.pack(fill="x", pady=(5, 0))
        self.generate_btn = ttk.Button(
            btn_frame, text="Сгенерировать", command=self._start_generation
        )
        self.generate_btn.pack(side="right")

        # ---- Прогресс-бар и статус ----
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.progress = ttk.Progressbar(
            progress_frame, mode="indeterminate", length=300
        )
        self.progress.pack(side="left", padx=(0, 10))

        self.status_var = tk.StringVar(value="Готов к работе")
        status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        status_label.pack(side="left", fill="x", expand=True)

        # ---- Панель предпросмотра ----
        preview_frame = ttk.LabelFrame(self.root, text="Предпросмотр", padding=10)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        preview_frame.columnconfigure(0, weight=1)
        preview_frame.columnconfigure(1, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        # Исходное изображение
        input_preview_frame = ttk.LabelFrame(preview_frame, text="Исходное")
        input_preview_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        input_preview_frame.columnconfigure(0, weight=1)
        input_preview_frame.rowconfigure(0, weight=1)

        self.input_canvas = tk.Canvas(
            input_preview_frame, bg="#f0f0f0", highlightthickness=0
        )
        self.input_canvas.pack(fill="both", expand=True)

        # Результирующее изображение
        output_preview_frame = ttk.LabelFrame(preview_frame, text="Результат")
        output_preview_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        output_preview_frame.columnconfigure(0, weight=1)
        output_preview_frame.rowconfigure(0, weight=1)

        self.output_canvas = tk.Canvas(
            output_preview_frame, bg="#f0f0f0", highlightthickness=0
        )
        self.output_canvas.pack(fill="both", expand=True)

        # Привязываем resize для обновления предпросмотра
        self.root.bind("<Configure>", self._on_resize)

    # ------------------------------------------------------------------
    #  Вспомогательные методы
    # ------------------------------------------------------------------

    def _browse_input(self):
        path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Изображения", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp"),
                ("Все файлы", "*.*"),
            ],
        )
        if path:
            self.input_image_path.set(path)
            self._show_preview_input(path)

    def _on_tab_change(self, event=None):
        """Переключение вкладки."""
        selected = self.notebook.select()
        for key, tab in self.tabs.items():
            if str(tab) == selected:
                self.current_tab = tab
                break

    def _show_preview_input(self, path):
        try:
            img = Image.open(path)
            self._display_on_canvas(img, self.input_canvas, "input")
        except Exception as e:
            self.status_var.set(f"Ошибка загрузки превью: {e}")

    def _show_preview_output(self, path):
        try:
            img = Image.open(path)
            self._display_on_canvas(img, self.output_canvas, "output")
        except Exception as e:
            self.status_var.set(f"Ошибка загрузки результата: {e}")

    def _display_on_canvas(self, img, canvas, key):
        canvas.update_idletasks()
        cw = canvas.winfo_width()
        ch = canvas.winfo_height()

        if cw < 10 or ch < 10:
            self.root.after(100, lambda: self._display_on_canvas(img, canvas, key))
            return

        img_w, img_h = img.size
        scale = min(cw / img_w, ch / img_h, 1.0)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)

        if new_w < 1 or new_h < 1:
            return

        resized = img.resize((new_w, new_h), Image.LANCZOS)
        photo = ImageTk.PhotoImage(resized)

        if key == "input":
            self.preview_input_tk = photo
        else:
            self.preview_output_tk = photo

        canvas.delete("all")
        x_center = cw // 2
        y_center = ch // 2
        canvas.create_image(x_center, y_center, image=photo, anchor="center")

    def _on_resize(self, event=None):
        if self.input_image_path.get() and os.path.exists(self.input_image_path.get()):
            self._show_preview_input(self.input_image_path.get())
        if hasattr(self, 'output_image_path') and self.output_image_path.get() and os.path.exists(self.output_image_path.get()):
            self._show_preview_output(self.output_image_path.get())

    # ------------------------------------------------------------------
    #  Генерация
    # ------------------------------------------------------------------

    def _start_generation(self):
        input_path = self.input_image_path.get().strip()
        if not input_path:
            messagebox.showwarning("Предупреждение", "Выберите входное изображение.")
            return
        if not os.path.isfile(input_path):
            messagebox.showerror("Ошибка", "Файл не найден.")
            return

        self.generate_btn.config(state="disabled")
        self.progress.start(10)
        self.status_var.set("Генерация...")

        thread = threading.Thread(target=self._generate, daemon=True)
        thread.start()

    def _generate(self):
        try:
            input_path = self.input_image_path.get().strip()
            output_name = self.output_name.get().strip() or "output"
            output_path = f"{output_name}.png"

            # Загружаем изображение
            self._update_status("Загрузка изображения...")
            gray = load_and_preprocess(input_path, 800)

            # Запускаем генерацию через активную вкладку
            self.current_tab.generate(gray, output_path, self._update_status)

            # Сохраняем путь для превью
            self.output_image_path = tk.StringVar(value=os.path.abspath(output_path))

            self.root.after(0, self._on_generation_done)

        except Exception as e:
            self.root.after(0, lambda: self._on_generation_error(str(e)))

    def _update_status(self, msg):
        self.root.after(0, lambda: self.status_var.set(msg))

    def _on_generation_done(self):
        self.progress.stop()
        self.generate_btn.config(state="normal")
        self.status_var.set("Готово!")

        out_path = self.output_image_path.get()
        if os.path.exists(out_path):
            self._show_preview_output(out_path)

        messagebox.showinfo("Успех", f"Изображение сохранено:\n{out_path}")

    def _on_generation_error(self, error_msg):
        self.progress.stop()
        self.generate_btn.config(state="normal")
        self.status_var.set("Ошибка")
        messagebox.showerror("Ошибка", error_msg)
