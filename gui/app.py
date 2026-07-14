"""
Spiral Line Art Generator — графическая оболочка на tkinter.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os

from PIL import Image, ImageTk

from spiral_generator import (
    load_and_preprocess,
    generate_spiral_path,
    generate_archimedean_spiral,
    generate_rectangular_spiral,
    draw_spiral_art,
)


class SpiralGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Spiral Line Art Generator")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Переменные для хранения путей к изображениям для предпросмотра
        self.input_image_path = tk.StringVar()
        self.output_image_path = tk.StringVar()
        self.preview_input_tk = None
        self.preview_output_tk = None

        self._build_ui()

    def _build_ui(self):
        # ---- Верхняя панель с параметрами ----
        top_frame = ttk.LabelFrame(self.root, text="Параметры", padding=10)
        top_frame.pack(fill="x", padx=10, pady=(10, 5))

        # Сетка параметров
        params_frame = ttk.Frame(top_frame)
        params_frame.pack(fill="x")

        # Строка 0: выбор входного файла
        ttk.Label(params_frame, text="Входное изображение:").grid(
            row=0, column=0, sticky="w", padx=(0, 5), pady=3
        )
        self.input_entry = ttk.Entry(
            params_frame, textvariable=self.input_image_path, width=50
        )
        self.input_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=3)
        ttk.Button(
            params_frame, text="Обзор...", command=self._browse_input
        ).grid(row=0, column=2, padx=(5, 0), pady=3)

        # Строка 1: имя выходного файла
        ttk.Label(params_frame, text="Выходной файл:").grid(
            row=1, column=0, sticky="w", padx=(0, 5), pady=3
        )
        self.output_entry = ttk.Entry(params_frame, width=50)
        self.output_entry.insert(0, "spiral_art")
        self.output_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=3)
        ttk.Label(params_frame, text="(без расширения)").grid(
            row=1, column=2, sticky="w", padx=(5, 0), pady=3
        )

        # Строка 2: тип спирали
        ttk.Label(params_frame, text="Тип спирали:").grid(
            row=2, column=0, sticky="w", padx=(0, 5), pady=3
        )
        self.spiral_type = tk.StringVar(value="archimedean")
        type_combo = ttk.Combobox(
            params_frame,
            textvariable=self.spiral_type,
            values=["archimedean", "elliptical", "rectangular"],
            state="readonly",
            width=20,
        )
        type_combo.grid(row=2, column=1, sticky="w", padx=5, pady=3)
        type_combo.bind("<<ComboboxSelected>>", self._on_type_change)

        # Строка 3: числовые параметры (первая строка)
        num_frame1 = ttk.Frame(params_frame)
        num_frame1.grid(row=3, column=0, columnspan=3, sticky="ew", pady=3)
        num_frame1.columnconfigure((1, 3, 5), weight=1)

        ttk.Label(num_frame1, text="Ширина:").grid(row=0, column=0, padx=(0, 2))
        self.width_var = tk.IntVar(value=800)
        ttk.Spinbox(
            num_frame1, from_=100, to=4000, textvariable=self.width_var, width=8
        ).grid(row=0, column=1, padx=(0, 15))

        ttk.Label(num_frame1, text="Витки:").grid(row=0, column=2, padx=(0, 2))
        self.turns_var = tk.IntVar(value=40)
        ttk.Spinbox(
            num_frame1, from_=5, to=500, textvariable=self.turns_var, width=8
        ).grid(row=0, column=3, padx=(0, 15))

        ttk.Label(num_frame1, text="Масштаб:").grid(row=0, column=4, padx=(0, 2))
        self.scale_var = tk.IntVar(value=2)
        ttk.Spinbox(
            num_frame1, from_=1, to=10, textvariable=self.scale_var, width=8
        ).grid(row=0, column=5, padx=(0, 15))

        # Строка 4: числовые параметры (вторая строка)
        num_frame2 = ttk.Frame(params_frame)
        num_frame2.grid(row=4, column=0, columnspan=3, sticky="ew", pady=3)
        num_frame2.columnconfigure((1, 3), weight=1)

        ttk.Label(num_frame2, text="Мин. толщина:").grid(row=0, column=0, padx=(0, 2))
        self.min_thick_var = tk.DoubleVar(value=0.5)
        ttk.Spinbox(
            num_frame2,
            from_=0.1,
            to=20.0,
            increment=0.1,
            textvariable=self.min_thick_var,
            width=8,
        ).grid(row=0, column=1, padx=(0, 15))

        ttk.Label(num_frame2, text="Макс. толщина:").grid(row=0, column=2, padx=(0, 2))
        self.max_thick_var = tk.DoubleVar(value=6.0)
        ttk.Spinbox(
            num_frame2,
            from_=0.1,
            to=20.0,
            increment=0.1,
            textvariable=self.max_thick_var,
            width=8,
        ).grid(row=0, column=3)

        # Кнопка генерации
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(fill="x", pady=(10, 0))
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

    def _show_preview_input(self, path):
        """Показывает превью исходного изображения на левом холсте."""
        try:
            img = Image.open(path)
            self._display_on_canvas(img, self.input_canvas, "input")
        except Exception as e:
            self.status_var.set(f"Ошибка загрузки превью: {e}")

    def _show_preview_output(self, path):
        """Показывает превью результата на правом холсте."""
        try:
            img = Image.open(path)
            self._display_on_canvas(img, self.output_canvas, "output")
        except Exception as e:
            self.status_var.set(f"Ошибка загрузки результата: {e}")

    def _display_on_canvas(self, img, canvas, key):
        """Масштабирует и отображает изображение на холсте."""
        # Получаем размеры холста
        canvas.update_idletasks()
        cw = canvas.winfo_width()
        ch = canvas.winfo_height()

        if cw < 10 or ch < 10:
            # Холст ещё не отрисован — отложим
            self.root.after(100, lambda: self._display_on_canvas(img, canvas, key))
            return

        # Масштабируем с сохранением пропорций
        img_w, img_h = img.size
        scale = min(cw / img_w, ch / img_h, 1.0)  # не увеличиваем
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)

        if new_w < 1 or new_h < 1:
            return

        resized = img.resize((new_w, new_h), Image.LANCZOS)

        # Конвертируем в PhotoImage
        photo = ImageTk.PhotoImage(resized)

        # Сохраняем ссылку, чтобы изображение не удалилось GC
        if key == "input":
            self.preview_input_tk = photo
        else:
            self.preview_output_tk = photo

        # Очищаем холст и рисуем
        canvas.delete("all")
        x_center = cw // 2
        y_center = ch // 2
        canvas.create_image(x_center, y_center, image=photo, anchor="center")

    def _on_resize(self, event=None):
        """Обновляет превью при изменении размера окна."""
        if self.input_image_path.get() and os.path.exists(self.input_image_path.get()):
            self._show_preview_input(self.input_image_path.get())
        if self.output_image_path.get() and os.path.exists(self.output_image_path.get()):
            self._show_preview_output(self.output_image_path.get())

    def _on_type_change(self, event=None):
        """Заглушка для смены типа спирали."""
        pass

    # ------------------------------------------------------------------
    #  Генерация
    # ------------------------------------------------------------------

    def _start_generation(self):
        """Запускает генерацию в отдельном потоке."""
        input_path = self.input_image_path.get().strip()
        if not input_path:
            messagebox.showwarning("Предупреждение", "Выберите входное изображение.")
            return
        if not os.path.isfile(input_path):
            messagebox.showerror("Ошибка", "Файл не найден.")
            return

        # Блокируем кнопку
        self.generate_btn.config(state="disabled")
        self.progress.start(10)
        self.status_var.set("Генерация...")

        # Запускаем в потоке
        thread = threading.Thread(target=self._generate, daemon=True)
        thread.start()

    def _generate(self):
        """Выполняет генерацию (вызывается в фоновом потоке)."""
        try:
            input_path = self.input_image_path.get().strip()
            output_name = self.output_entry.get().strip() or "spiral_art"
            width = self.width_var.get()
            turns = self.turns_var.get()
            min_thick = self.min_thick_var.get()
            max_thick = self.max_thick_var.get()
            scale = self.scale_var.get()
            spiral_type = self.spiral_type.get()

            # Загружаем и препроцессим
            self._update_status("Загрузка изображения...")
            gray = load_and_preprocess(input_path, width)
            h, w = gray.shape

            # Генерируем спираль
            self._update_status(f"Генерация спирали ({spiral_type})...")
            if spiral_type == "archimedean":
                spiral_points = generate_archimedean_spiral(w, h, turns)
            elif spiral_type == "elliptical":
                spiral_points = generate_spiral_path(w, h, turns)
            elif spiral_type == "rectangular":
                spiral_points = generate_rectangular_spiral(w, h, turns)
            else:
                raise ValueError(f"Неизвестный тип спирали: {spiral_type}")

            # Рисуем
            self._update_status("Отрисовка...")
            output_path = f"{output_name}.png"
            draw_spiral_art(
                gray, spiral_points, output_path,
                min_thick, max_thick, scale
            )

            # Сохраняем путь для превью
            self.output_image_path.set(os.path.abspath(output_path))

            # Обновляем превью в главном потоке
            self.root.after(0, self._on_generation_done)

        except Exception as e:
            self.root.after(0, lambda: self._on_generation_error(str(e)))

    def _update_status(self, msg):
        """Безопасно обновляет статус из фонового потока."""
        self.root.after(0, lambda: self.status_var.set(msg))

    def _on_generation_done(self):
        """Вызывается в главном потоке после успешной генерации."""
        self.progress.stop()
        self.generate_btn.config(state="normal")
        self.status_var.set("Готово!")

        # Показываем превью результата
        out_path = self.output_image_path.get()
        if os.path.exists(out_path):
            self._show_preview_output(out_path)

        messagebox.showinfo("Успех", f"Изображение сохранено:\n{out_path}")

    def _on_generation_error(self, error_msg):
        """Вызывается в главном потоке при ошибке."""
        self.progress.stop()
        self.generate_btn.config(state="normal")
        self.status_var.set("Ошибка")
        messagebox.showerror("Ошибка", error_msg)
