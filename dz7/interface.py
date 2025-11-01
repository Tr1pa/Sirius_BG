import tkinter as tk
from tkinter import ttk, messagebox
from main import OneHeapGameSolver, TwoHeapGameSolver

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализатор Теории Игр")
        self.root.geometry("650x700")

        # --- Стили ---
        style = ttk.Style()
        style.configure("TLabel", padding=5, font=("Helvetica", 11))
        style.configure("TButton", padding=5, font=("Helvetica", 11, "bold"))
        style.configure("TEntry", padding=5, font=("Helvetica", 11))
        style.configure("Header.TLabel", font=("Helvetica", 13, "bold"))
        style.configure("Result.TLabel", font=("Courier", 12), foreground="navy", wraplength=580)
        style.configure("TRadiobutton", font=("Helvetica", 11))
        style.configure("Desc.TLabel", font=("Helvetica", 9), foreground="gray")

        # --- Выбор режима игры ---
        mode_frame = ttk.LabelFrame(root, text="Режим игры", padding=10)
        mode_frame.pack(padx=10, pady=10, fill="x")
        self.game_mode = tk.StringVar(value="one_heap")
        
        ttk.Radiobutton(mode_frame, text="Одна куча", variable=self.game_mode, value="one_heap", command=self._update_ui).pack(side="left", padx=10)
        ttk.Radiobutton(mode_frame, text="Две кучи", variable=self.game_mode, value="two_heaps", command=self._update_ui).pack(side="left", padx=10)

        # --- Фреймы для параметров ---
        self.one_heap_frame = self._create_one_heap_params_frame(root)
        self.two_heaps_frame = self._create_two_heaps_params_frame(root)

        # --- Выбор типа задания ---
        task_frame = ttk.LabelFrame(root, text="Тип задания", padding=10)
        task_frame.pack(padx=10, pady=5, fill="x")
        self.task_type = tk.StringVar(value="19")
        
        ttk.Radiobutton(task_frame, text="№19 (Ваня выигрывает 1-м ходом после неудачного хода Пети)", variable=self.task_type, value="19").pack(anchor="w")
        ttk.Radiobutton(task_frame, text="№20 (Петя выигрывает 2-м ходом, но не 1-м)", variable=self.task_type, value="20").pack(anchor="w")
        ttk.Radiobutton(task_frame, text="№21 (Ваня выигрывает 1-м/2-м ходом, но не гарантированно 1-м)", variable=self.task_type, value="21").pack(anchor="w")

        # --- Кнопка и результаты ---
        self.calc_button = ttk.Button(root, text="Рассчитать", command=self.run_analysis)
        self.calc_button.pack(pady=10)
        
        self.result_frame = self._create_results_frame(root)
        self._update_ui()

    def _create_one_heap_params_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Параметры для одной кучи", padding=10)
        
        ttk.Label(frame, text="Победа, если камней >=").grid(row=0, column=0, sticky="w", pady=2)
        self.oh_win_entry = ttk.Entry(frame, width=10)
        self.oh_win_entry.insert(0, "41")
        self.oh_win_entry.grid(row=0, column=1, padx=5)

        self.oh_is_subtractive = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Игра на уменьшение (победа <=)", variable=self.oh_is_subtractive).grid(row=0, column=2, columnspan=2, sticky="w")

        ttk.Label(frame, text="Диапазон S: от").grid(row=1, column=0, sticky="w", pady=2)
        self.oh_s_min_entry = ttk.Entry(frame, width=5)
        self.oh_s_min_entry.insert(0, "1")
        self.oh_s_min_entry.grid(row=1, column=1, sticky="w", padx=5)
        ttk.Label(frame, text="до").grid(row=1, column=2, sticky="w")
        self.oh_s_max_entry = ttk.Entry(frame, width=5)
        self.oh_s_max_entry.insert(0, "40")
        self.oh_s_max_entry.grid(row=1, column=3, sticky="w", padx=5)

        ttk.Label(frame, text="Возможные ходы:").grid(row=2, column=0, sticky="w", pady=2)
        self.oh_moves_entry = ttk.Entry(frame, width=25)
        self.oh_moves_entry.insert(0, "+1, +4, *3")
        self.oh_moves_entry.grid(row=2, column=1, columnspan=3, sticky="w", padx=5)
        ttk.Label(frame, text="Пример: +1, *2, -3, /2 (или n/k для спец. правил)", style="Desc.TLabel").grid(row=3, column=1, columnspan=3, sticky="w", padx=5)

        return frame

    def _create_two_heaps_params_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Параметры для двух куч", padding=10)

        ttk.Label(frame, text="Сумма для победы >=").grid(row=0, column=0, sticky="w", pady=2)
        self.th_win_entry = ttk.Entry(frame, width=10)
        self.th_win_entry.insert(0, "82")
        self.th_win_entry.grid(row=0, column=1, padx=5)

        self.th_is_subtractive = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Игра на уменьшение (победа <=)", variable=self.th_is_subtractive).grid(row=0, column=2, columnspan=2, sticky="w")

        ttk.Label(frame, text="Камней в 1-й (фикс.) куче:").grid(row=1, column=0, sticky="w", pady=2)
        self.th_fixed_heap_entry = ttk.Entry(frame, width=10)
        self.th_fixed_heap_entry.insert(0, "4")
        self.th_fixed_heap_entry.grid(row=1, column=1, padx=5)

        ttk.Label(frame, text="Диапазон S (2-я куча): от").grid(row=2, column=0, sticky="w", pady=2)
        self.th_s_min_entry = ttk.Entry(frame, width=5)
        self.th_s_min_entry.insert(0, "1")
        self.th_s_min_entry.grid(row=2, column=1, sticky="w", padx=5)
        ttk.Label(frame, text="до").grid(row=2, column=2, sticky="w")
        self.th_s_max_entry = ttk.Entry(frame, width=5)
        self.th_s_max_entry.insert(0, "77")
        self.th_s_max_entry.grid(row=2, column=3, sticky="w", padx=5)

        ttk.Label(frame, text="Возможные ходы:").grid(row=3, column=0, sticky="w", pady=2)
        self.th_moves_entry = ttk.Entry(frame, width=45)
        self.th_moves_entry.insert(0, "+1 H_any, *4 H_any")
        self.th_moves_entry.grid(row=3, column=1, columnspan=3, sticky="w", padx=5)
        ttk.Label(frame, text="Синтаксис: +1 H1, *2 H2, +1 H_any, +1 H_smaller, +1 H1 +2 H2", style="Desc.TLabel").grid(row=4, column=1, columnspan=3, sticky="w", padx=5)

        return frame

    def _create_results_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Результаты", padding=10)
        frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.result_label = ttk.Label(frame, text="...", style="Result.TLabel", anchor="nw")
        self.result_label.pack(fill="both", expand=True, pady=5, padx=5)
        return frame
        
    def _update_ui(self):
        if self.game_mode.get() == "one_heap":
            self.two_heaps_frame.pack_forget()
            self.one_heap_frame.pack(padx=10, pady=5, fill="x")
        else:
            self.one_heap_frame.pack_forget()
            self.two_heaps_frame.pack(padx=10, pady=5, fill="x")

    def run_analysis(self):
        try:
            task = self.task_type.get()
            
            if self.game_mode.get() == "one_heap":
                win_cond = int(self.oh_win_entry.get())
                s_min = int(self.oh_s_min_entry.get())
                s_max = int(self.oh_s_max_entry.get())
                moves = self.oh_moves_entry.get()
                is_sub = self.oh_is_subtractive.get()
                solver = OneHeapGameSolver(win_cond, s_min, s_max, moves, is_subtractive=is_sub)
            else:
                win_cond = int(self.th_win_entry.get())
                fixed_heap = int(self.th_fixed_heap_entry.get())
                s_min = int(self.th_s_min_entry.get())
                s_max = int(self.th_s_max_entry.get())
                moves = self.th_moves_entry.get()
                is_sub = self.th_is_subtractive.get()
                solver = TwoHeapGameSolver(win_cond, fixed_heap, s_min, s_max, moves, is_subtractive=is_sub)

            self.root.config(cursor="watch")
            self.root.update()
            
            result = solver.solve(task)
            
            self.root.config(cursor="")
            result_text = f"Найденные значения S для задания типа №{task}:\n"
            if result:
                result_text += str(result)
                if len(result) > 0:
                    result_text += f"\n\nМинимальное: {min(result)}"
                    result_text += f"\nМаксимальное: {max(result)}"
                    result_text += f"\nКоличество: {len(result)}"
            else:
                result_text += "Решений не найдено."
            self.result_label.config(text=result_text)

        except ValueError:
            self.root.config(cursor="")
            messagebox.showerror("Ошибка ввода", "Все числовые параметры должны быть целыми числами.")
        except Exception as e:
            self.root.config(cursor="")
            messagebox.showerror("Ошибка выполнения", f"Произошла ошибка: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()