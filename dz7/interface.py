# interface.py
import tkinter as tk
from tkinter import ttk, messagebox
from main import OneHeapGameSolver, TwoHeapGameSolver

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализатор Теории Игр")
        self.root.geometry("600x600")

        # --- Стили ---
        style = ttk.Style()
        style.configure("TLabel", padding=5, font=("Helvetica", 11))
        style.configure("TButton", padding=5, font=("Helvetica", 11, "bold"))
        style.configure("TEntry", padding=5, font=("Helvetica", 11))
        style.configure("Header.TLabel", font=("Helvetica", 13, "bold"))
        style.configure("Result.TLabel", font=("Courier", 12), foreground="navy")
        style.configure("TRadiobutton", font=("Helvetica", 11))

        # --- Выбор режима игры ---
        mode_frame = ttk.LabelFrame(root, text="Режим игры", padding=10)
        mode_frame.pack(padx=10, pady=10, fill="x")
        self.game_mode = tk.StringVar(value="one_heap")
        
        ttk.Radiobutton(mode_frame, text="Одна куча", variable=self.game_mode, value="one_heap", command=self._update_ui).pack(side="left", padx=10)
        ttk.Radiobutton(mode_frame, text="Две кучи", variable=self.game_mode, value="two_heaps", command=self._update_ui).pack(side="left", padx=10)

        # --- Фреймы для параметров (будем переключать их видимость) ---
        self.one_heap_frame = self._create_one_heap_params_frame(root)
        self.two_heaps_frame = self._create_two_heaps_params_frame(root)

        # --- Кнопка и результаты ---
        self.calc_button = ttk.Button(root, text="Рассчитать", command=self.run_analysis)
        self.calc_button.pack(pady=10)
        
        self.result_frame = self._create_results_frame(root)
        
        # Инициализация UI
        self._update_ui()

    def _create_one_heap_params_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Параметры для одной кучи", padding=10)
        
        ttk.Label(frame, text="Победа, если камней ≥").grid(row=0, column=0, sticky="w")
        self.oh_win_entry = ttk.Entry(frame, width=10)
        self.oh_win_entry.insert(0, "77")
        self.oh_win_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(frame, text="Диапазон S: от").grid(row=1, column=0, sticky="w")
        self.oh_s_min_entry = ttk.Entry(frame, width=5)
        self.oh_s_min_entry.insert(0, "1")
        self.oh_s_min_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        ttk.Label(frame, text="до").grid(row=1, column=2, sticky="w")
        self.oh_s_max_entry = ttk.Entry(frame, width=5)
        self.oh_s_max_entry.insert(0, "68")
        self.oh_s_max_entry.grid(row=1, column=3, sticky="w", padx=5, pady=2)
        return frame

    def _create_two_heaps_params_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Параметры для двух куч", padding=10)

        ttk.Label(frame, text="Сумма для победы ≥").grid(row=0, column=0, sticky="w")
        self.th_win_entry = ttk.Entry(frame, width=10)
        self.th_win_entry.insert(0, "77")
        self.th_win_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(frame, text="Камней в 1-й (фикс.) куче:").grid(row=1, column=0, sticky="w")
        self.th_fixed_heap_entry = ttk.Entry(frame, width=10)
        self.th_fixed_heap_entry.insert(0, "8")
        self.th_fixed_heap_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(frame, text="Диапазон S (2-я куча): от").grid(row=2, column=0, sticky="w")
        self.th_s_min_entry = ttk.Entry(frame, width=5)
        self.th_s_min_entry.insert(0, "1")
        self.th_s_min_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        ttk.Label(frame, text="до").grid(row=2, column=2, sticky="w")
        self.th_s_max_entry = ttk.Entry(frame, width=5)
        self.th_s_max_entry.insert(0, "68")
        self.th_s_max_entry.grid(row=2, column=3, sticky="w", padx=5, pady=2)
        return frame

    def _create_results_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Результаты", padding=10)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        ttk.Label(frame, text="Задание 19 (результат m1):", style="Header.TLabel").pack(anchor="w")
        self.res1_label = ttk.Label(frame, text="...", style="Result.TLabel")
        self.res1_label.pack(anchor="w", pady=(0, 15), padx=5)
        
        ttk.Label(frame, text="Задание 20 (результат m2):", style="Header.TLabel").pack(anchor="w")
        self.res2_label = ttk.Label(frame, text="...", style="Result.TLabel")
        self.res2_label.pack(anchor="w", pady=(0, 15), padx=5)
        
        ttk.Label(frame, text="Задание 21 (результат m3):", style="Header.TLabel").pack(anchor="w")
        self.res3_label = ttk.Label(frame, text="...", style="Result.TLabel")
        self.res3_label.pack(anchor="w", pady=(0, 15), padx=5)
        return frame
        
    def _update_ui(self):
        """Показывает/скрывает фреймы с параметрами в зависимости от режима."""
        if self.game_mode.get() == "one_heap":
            self.two_heaps_frame.pack_forget()
            self.one_heap_frame.pack(padx=10, fill="x")
        else:
            self.one_heap_frame.pack_forget()
            self.two_heaps_frame.pack(padx=10, fill="x")

    def run_analysis(self):
        try:
            if self.game_mode.get() == "one_heap":
                win_cond = int(self.oh_win_entry.get())
                s_min = int(self.oh_s_min_entry.get())
                s_max = int(self.oh_s_max_entry.get())
                solver = OneHeapGameSolver(win_cond, s_min, s_max)
            else: # two_heaps
                win_cond = int(self.th_win_entry.get())
                fixed_heap = int(self.th_fixed_heap_entry.get())
                s_min = int(self.th_s_min_entry.get())
                s_max = int(self.th_s_max_entry.get())
                solver = TwoHeapGameSolver(win_cond, fixed_heap, s_min, s_max)

            m1, m2, m3 = solver.start()
            
            # Обновляем поля результатов
            self.res1_label.config(text=str(m1) if m1 else "Решений не найдено.")
            self.res2_label.config(text=str(m2) if m2 else "Решений не найдено.")
            self.res3_label.config(text=str(m3) if m3 else "Решений не найдено.")

        except ValueError:
            messagebox.showerror("Ошибка ввода", "Все параметры должны быть целыми числами.")
        except Exception as e:
            messagebox.showerror("Ошибка выполнения", f"Произошла ошибка: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()