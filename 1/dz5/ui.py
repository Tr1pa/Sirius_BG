import tkinter as tk
from tkinter import ttk, messagebox
from script import TruthTableCalculator


class TruthTableApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Truth Project")
        self.root.geometry("900x700")

        self.calculator = TruthTableCalculator()
        self.current_filter = 'all'
        self.edit_mode = False
        self.edited_results = None

        self._create_widgets()

    def _create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        normal_frame = ttk.Frame(notebook)
        ege_frame = ttk.Frame(notebook)

        notebook.add(normal_frame, text="Таблица истинности")
        notebook.add(ege_frame, text="Решатель ЕГЭ")

        self._setup_normal_tab(normal_frame)
        self._setup_ege_tab(ege_frame)

    def _setup_normal_tab(self, parent: ttk.Frame):
        tk.Label(parent, text="Генератор таблицы истинности", font=("Arial", 16, "bold")).pack(pady=10)

        input_frame = ttk.Frame(parent)
        input_frame.pack(pady=10, padx=20, fill="x")
        tk.Label(input_frame, text="Выражение (используйте x, y, z, w и синтаксис Python):").pack(anchor="w")
        self.expression_entry = ttk.Entry(input_frame, font=("Arial", 12))
        self.expression_entry.pack(fill="x", pady=5)
        self.expression_entry.bind("<Return>", lambda event: self._calculate_table())

        example_frame = ttk.Frame(input_frame)
        example_frame.pack(fill="x", pady=5)
        examples = ["(x and not y) or (y == z) or w", "x or y", "not w", "(x or y) and (not z)"]
        for example in examples:
            btn = ttk.Button(example_frame, text=example, command=lambda e=example: self._set_example(self.expression_entry, e))
            btn.pack(side="left", padx=2)

        control_frame = ttk.Frame(parent)
        control_frame.pack(pady=10)
        ttk.Button(control_frame, text="Вычислить", command=self._calculate_table).pack(side="left", padx=5)
        
        self.edit_var = tk.BooleanVar()
        ttk.Checkbutton(control_frame, text="Режим редактирования", variable=self.edit_var, command=self._toggle_edit_mode).pack(side="left", padx=10)
        
        self.restore_btn = ttk.Button(control_frame, text="Восстановить выражение", command=self._restore_expression, state="disabled")
        self.restore_btn.pack(side="left", padx=5)

        filter_frame = ttk.Frame(parent)
        filter_frame.pack(pady=5)
        tk.Label(filter_frame, text="Фильтры:").pack(side="left")
        filters = [("Все", "all"), ("True", "true"), ("False", "false"), ("Меньшинство", "minority")]
        for text, f_type in filters:
            ttk.Button(filter_frame, text=text, command=lambda f=f_type: self._apply_filter(f)).pack(side="left", padx=2)

        table_frame = ttk.Frame(parent)
        table_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.tree = ttk.Treeview(table_frame, show="headings", height=10)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", self._edit_result_cell)
        
        self.info_label = ttk.Label(parent, text="", foreground="blue")
        self.info_label.pack(pady=5)

    def _set_example(self, entry_widget: ttk.Entry, example: str):
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, example)

    def _calculate_table(self):
        expression = self.expression_entry.get().strip()
        if not expression:
            messagebox.showwarning("Внимание", "Введите выражение.")
            return
        try:
            self.calculator.build_truth_table(expression)
            self.edited_results = None
            self.edit_var.set(False)
            self._toggle_edit_mode()
            self._apply_filter('all')
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def _apply_filter(self, filter_type: str):
        self.current_filter = filter_type
        self._update_table_display()

    def _update_table_display(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        source_results = self.edited_results if self.edited_results is not None else self.calculator.full_table
        if not source_results:
            self._update_info_label()
            return
        
        results_to_show = source_results
        true_count = sum(1 for r in source_results if r['result'])
        false_count = len(source_results) - true_count

        if self.current_filter == 'true':
            results_to_show = [r for r in source_results if r['result']]
        elif self.current_filter == 'false':
            results_to_show = [r for r in source_results if not r['result']]
        elif self.current_filter == 'minority':
            if true_count < false_count:
                results_to_show = [r for r in source_results if r['result']]
            elif false_count < true_count:
                results_to_show = [r for r in source_results if not r['result']]

        variables = self.calculator.variables
        self.tree['columns'] = variables + ['Результат']
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor="center")

        for result in results_to_show:
            values = [result.get(var, '') for var in variables] + [result['result']]
            self.tree.insert("", "end", values=tuple(values))

        self._update_info_label()

    def _update_info_label(self):
        source_results = self.edited_results if self.edited_results is not None else self.calculator.full_table
        if not source_results:
            self.info_label.config(text="")
            return

        total = len(source_results)
        true_count = sum(1 for r in source_results if r['result'])
        false_count = total - true_count
        
        minority = "Равное количество"
        if true_count < false_count:
            minority = f"True в меньшинстве ({true_count})"
        elif false_count < true_count:
            minority = f"False в меньшинстве ({false_count})"

        self.info_label.config(text=f"Всего: {total} | True: {true_count} | False: {false_count} | {minority} | Фильтр: {self.current_filter}")

    def _toggle_edit_mode(self):
        self.edit_mode = self.edit_var.get()
        self.restore_btn.config(state="normal" if self.edit_mode else "disabled")
        if not self.edit_mode:
            self.edited_results = None
            self._update_table_display()

    def _edit_result_cell(self, event):
        if not self.edit_mode or not self.calculator.full_table: return
        selection = self.tree.selection()
        if not selection: return

        if self.edited_results is None:
            self.edited_results = [r.copy() for r in self.calculator.full_table]
        
        selected_item = self.tree.item(selection[0], "values")
        
        for result in self.edited_results:
            matches = all(str(result.get(var, '')) == str(selected_item[i]) for i, var in enumerate(self.calculator.variables))
            if matches:
                result['result'] = not result['result']
                break
        
        self._update_table_display()

    def _restore_expression(self):
        if self.edited_results is None:
            messagebox.showinfo("Инфо", "Нет изменений для восстановления.")
            return
        
        try:
            expression = self.calculator.generate_expression_from_table(self.edited_results)
            self._show_restored_expression_dialog(expression)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать выражение: {e}")
            
    def _show_restored_expression_dialog(self, expression: str):
        dialog = tk.Toplevel(self.root)
        dialog.title("Восстановленное выражение")
        dialog.geometry("400x200")
        
        tk.Label(dialog, text="Восстановленное выражение (ДНФ):", font=("Arial", 12, "bold")).pack(pady=10)
        text_widget = tk.Text(dialog, height=5, wrap=tk.WORD, font=("Consolas", 10))
        text_widget.pack(pady=10, padx=20, fill="both", expand=True)
        text_widget.insert("1.0", expression)
        text_widget.config(state="disabled")
        
        def use_expression():
            self._set_example(self.expression_entry, expression)
            dialog.destroy()
            self._calculate_table()

        ttk.Button(dialog, text="Использовать это выражение", command=use_expression).pack(pady=5)

    def _setup_ege_tab(self, parent: ttk.Frame):
        tk.Label(parent, text="Решатель задач ЕГЭ (задание 2)", font=("Arial", 16, "bold")).pack(pady=10)
        instruction = "Введите выражение (переменные x, y, z, w).\nЗаполните неполную таблицу. Для неизвестных значений оставьте ячейку пустой."
        tk.Label(parent, text=instruction, font=("Arial", 10)).pack(pady=5)

        input_frame = ttk.Frame(parent)
        input_frame.pack(pady=10, padx=20, fill="x")
        tk.Label(input_frame, text="Логическое выражение:").pack(anchor="w")
        self.ege_expression_entry = ttk.Entry(input_frame, font=("Arial", 12))
        self.ege_expression_entry.pack(fill="x", pady=2)
        ege_example = "(x and not y) or (y == z) or w"
        ttk.Button(input_frame, text=f"Пример: {ege_example}", command=lambda: self._set_example(self.ege_expression_entry, ege_example)).pack(anchor="w", pady=5)
        
        ttk.Button(input_frame, text="Решить задачу", command=self._solve_ege_task).pack(fill="x", pady=10)

        tables_frame = ttk.Frame(parent)
        tables_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        left_frame = ttk.Frame(tables_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right_frame = ttk.Frame(tables_frame)
        right_frame.pack(side="right", fill="both", expand=True)
        
        tk.Label(left_frame, text="Неполная таблица истинности:", font=("Arial", 12, "bold")).pack(anchor="w")
        ege_columns = ("F1", "F2", "F3", "F4", "Результат")
        self.ege_input_tree = ttk.Treeview(left_frame, columns=ege_columns, show="headings", height=8)
        for col in ege_columns:
            self.ege_input_tree.heading(col, text=col)
            self.ege_input_tree.column(col, width=60, anchor="center")
        self.ege_input_tree.pack(fill="both", expand=True)
        self.ege_input_tree.bind("<Double-1>", self._edit_ege_cell)

        table_controls = ttk.Frame(left_frame)
        table_controls.pack(fill="x", pady=5)
        ttk.Button(table_controls, text="Добавить строку", command=self._add_ege_row).pack(side="left")
        ttk.Button(table_controls, text="Удалить строку", command=self._delete_ege_row).pack(side="left", padx=5)
        ttk.Button(table_controls, text="Очистить", command=self._clear_ege_table).pack(side="left")

        tk.Label(right_frame, text="Результаты решения:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.ege_results_text = tk.Text(right_frame, height=15, wrap=tk.WORD, font=("Consolas", 11))
        ege_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.ege_results_text.yview)
        self.ege_results_text.configure(yscrollcommand=ege_scrollbar.set)
        self.ege_results_text.pack(side="left", fill="both", expand=True)
        ege_scrollbar.pack(side="right", fill="y")
        self.ege_results_text.config(state="disabled")

    def _solve_ege_task(self):
        expression = self.ege_expression_entry.get().strip()
        if not expression:
            messagebox.showwarning("Внимание", "Введите выражение.")
            return

        partial_table = []
        for item in self.ege_input_tree.get_children():
            values = self.ege_input_tree.item(item, "values")
            try:
                row = {
                    'F1': int(values[0]) if values[0] else None,
                    'F2': int(values[1]) if values[1] else None,
                    'F3': int(values[2]) if values[2] else None,
                    'F4': int(values[3]) if values[3] else None,
                    'result': bool(int(values[4]))
                }
                partial_table.append(row)
            except (ValueError, IndexError):
                messagebox.showerror("Ошибка", "Все значения в таблице должны быть 0, 1 или пустыми, а 'Результат' должен быть 0 или 1.")
                return
        
        if not partial_table:
            messagebox.showwarning("Внимание", "Заполните таблицу.")
            return
        
        try:
            solutions = self.calculator.solve_ege_task(expression, partial_table)
            self._display_ege_solutions(solutions)
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def _display_ege_solutions(self, solutions: list[str]):
        """Форматирует и выводит найденные решения в текстовое поле."""
        self.ege_results_text.config(state="normal")
        self.ege_results_text.delete("1.0", tk.END)
        if not solutions:
            self.ege_results_text.insert("1.0", "Решений не найдено.\n\nПроверьте правильность выражения и таблицы.")
        else:
            self.ege_results_text.insert("1.0", f"Найдено возможных решений: {len(solutions)}\n\n")
            for i, solution in enumerate(solutions, 1):
                self.ege_results_text.insert(tk.END, f"Решение {i}: {solution}\n")
            if len(solutions) == 1:
                self.ege_results_text.insert(tk.END, "\n✓ Найдено единственное решение!")
        self.ege_results_text.config(state="disabled")

    def _add_ege_row(self):
        self.ege_input_tree.insert("", "end", values=("", "", "", "", "0"))

    def _delete_ege_row(self):
        if selection := self.ege_input_tree.selection():
            self.ege_input_tree.delete(selection[0])
            
    def _clear_ege_table(self):
        for item in self.ege_input_tree.get_children():
            self.ege_input_tree.delete(item)

    def _edit_ege_cell(self, event):
        """Редактирует ячейку в таблице ЕГЭ по двойному клику."""
        if not (selection := self.ege_input_tree.selection()): return
        
        item = selection[0]
        col_id_str = self.ege_input_tree.identify_column(event.x)
        
        try:
            col_index = int(col_id_str.replace('#', '')) - 1
            values = list(self.ege_input_tree.item(item, "values"))

            if 0 <= col_index < 4:
                current_value = values[col_index]
                values[col_index] = "1" if current_value == "0" else "" if current_value == "1" else "0"
            elif col_index == 4:
                values[col_index] = "1" if values[col_index] == "0" else "0"
                
            self.ege_input_tree.item(item, values=values)
        except (ValueError, IndexError):
            pass # Клик вне ячеек


def main():
    """Главная функция для запуска приложения."""
    root = tk.Tk()
    app = TruthTableApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()