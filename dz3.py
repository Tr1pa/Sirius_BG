import tkinter as tk

# ==========================================
# ЧАСТЬ 1: Логическое ядро (Ваши классы, немного доработанные)
# ==========================================

class TLogElement:
    def __init__(self, name=""):
        self._in1 = False
        self._in2 = False
        self._res = False
        self.name = name
        self.next_el = None
        self.next_pin = 0
        
    @property
    def Res(self):
        return self._res

    # Метод для принудительного обновления (используется GUI)
    def set_in1(self, val):
        self._in1 = val
        self.calc()
        self.propagate()

    def set_in2(self, val):
        self._in2 = val
        self.calc()
        self.propagate()
        
    # Свойства для связывания (как в оригинале)
    In1 = property(lambda self: self._in1, set_in1)
    In2 = property(lambda self: self._in2, set_in2)

    def link(self, next_el, next_pin):
        self.next_el = next_el
        self.next_pin = next_pin

    def propagate(self):
        # Передача сигнала следующему элементу
        if self.next_el:
            if self.next_pin == 1:
                self.next_el.In1 = self._res
            elif self.next_pin == 2:
                self.next_el.In2 = self._res

    def calc(self):
        raise NotImplementedError

class TNot(TLogElement):
    def calc(self):
        self._res = not self._in1

class TAnd(TLogElement):
    def calc(self):
        self._res = self._in1 and self._in2

class TOr(TLogElement):
    def calc(self):
        self._res = self._in1 or self._in2

# ==========================================
# ЧАСТЬ 2: Графический интерфейс (Tkinter)
# ==========================================

class LogicCircuitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Визуализатор Логической Схемы (XOR)")
        
        # Настройка холста
        self.canvas = tk.Canvas(root, width=600, height=400, bg="white")
        self.canvas.pack(pady=10)
        
        # Элементы управления
        control_frame = tk.Frame(root)
        control_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.var_x = tk.BooleanVar()
        self.var_y = tk.BooleanVar()
        
        tk.Checkbutton(control_frame, text="Вход X", variable=self.var_x, 
                       command=self.update_circuit, font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=20)
        tk.Checkbutton(control_frame, text="Вход Y", variable=self.var_y, 
                       command=self.update_circuit, font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=20)
        
        self.lbl_result = tk.Label(control_frame, text="Результат: 0", font=("Arial", 14, "bold"), fg="blue")
        self.lbl_result.pack(side=tk.RIGHT, padx=20)

        # Инициализация схемы
        self.setup_circuit()
        self.update_circuit()

    def setup_circuit(self):
        # 1. Создаем логические элементы
        self.not_top = TNot("NOT_TOP")
        self.and_top = TAnd("AND_TOP")
        self.not_bottom = TNot("NOT_BOT")
        self.and_bottom = TAnd("AND_BOT")
        self.or_final = TOr("OR_RES")

        # 2. Связываем их (как в вашем коде)
        # Верхняя ветка: NOT(Y) -> AND(X, ...)
        self.not_top.link(self.and_top, 2)
        self.and_top.link(self.or_final, 1)

        # Нижняя ветка: NOT(X) -> AND(..., Y)
        self.not_bottom.link(self.and_bottom, 1)
        self.and_bottom.link(self.or_final, 2)

        # Координаты для рисования (x, y)
        self.positions = {
            "InputX": (50, 100),
            "InputY": (50, 300),
            "NOT_TOP": (150, 250), # Инвертирует Y для верхнего И
            "NOT_BOT": (150, 150), # Инвертирует X для нижнего И
            "AND_TOP": (300, 100),
            "AND_BOT": (300, 300),
            "OR_RES":  (500, 200)
        }

    def update_circuit(self):
        # Сброс холста
        self.canvas.delete("all")
        
        x_val = self.var_x.get()
        y_val = self.var_y.get()

        # ВНИМАНИЕ: Ручная подача сигналов, так как схема сложная (перекрестная)
        
        # 1. Вход X идет в AND_TOP (pin 1) и в NOT_BOT (pin 1)
        self.and_top.In1 = x_val
        self.not_bottom.In1 = x_val
        
        # 2. Вход Y идет в NOT_TOP (pin 1) и в AND_BOTTOM (pin 2)
        self.not_top.In1 = y_val
        self.and_bottom.In2 = y_val
        
        # Результат
        res = self.or_final.Res
        self.lbl_result.config(text=f"Результат: {int(res)}", fg=("green" if res else "red"))

        # === ОТРИСОВКА ===
        
        # Рисуем провода (сначала провода, чтобы они были под блоками)
        # X -> AND_TOP (pin 1)
        self.draw_wire(self.positions["InputX"], self.positions["AND_TOP"], x_val, offset_target_y=-10)
        # X -> NOT_BOT
        self.draw_wire(self.positions["InputX"], self.positions["NOT_BOT"], x_val)
        
        # Y -> NOT_TOP
        self.draw_wire(self.positions["InputY"], self.positions["NOT_TOP"], y_val)
        # Y -> AND_BOT (pin 2)
        self.draw_wire(self.positions["InputY"], self.positions["AND_BOT"], y_val, offset_target_y=10)

        # NOT_TOP -> AND_TOP (pin 2)
        self.draw_wire(self.positions["NOT_TOP"], self.positions["AND_TOP"], self.not_top.Res, offset_target_y=10)
        
        # NOT_BOT -> AND_BOTTOM (pin 1)
        self.draw_wire(self.positions["NOT_BOT"], self.positions["AND_BOT"], self.not_bottom.Res, offset_target_y=-10)
        
        # AND_TOP -> OR
        self.draw_wire(self.positions["AND_TOP"], self.positions["OR_RES"], self.and_top.Res, offset_target_y=-10)
        
        # AND_BOT -> OR
        self.draw_wire(self.positions["AND_BOT"], self.positions["OR_RES"], self.and_bottom.Res, offset_target_y=10)

        # Рисуем узлы и элементы
        self.draw_node("Вход X", self.positions["InputX"], x_val)
        self.draw_node("Вход Y", self.positions["InputY"], y_val)
        
        self.draw_gate("NOT", self.positions["NOT_TOP"], self.not_top.Res)
        self.draw_gate("NOT", self.positions["NOT_BOT"], self.not_bottom.Res)
        self.draw_gate("AND", self.positions["AND_TOP"], self.and_top.Res)
        self.draw_gate("AND", self.positions["AND_BOT"], self.and_bottom.Res)
        self.draw_gate("OR",  self.positions["OR_RES"],  self.or_final.Res, is_final=True)

    def get_color(self, state):
        return "#32CD32" if state else "#A9A9A9"  # LimeGreen или DarkGray

    def draw_wire(self, start, end, state, offset_target_y=0):
        color = self.get_color(state)
        # Рисуем линию "ступенькой" для красоты
        x1, y1 = start
        x2, y2 = end
        y2 += offset_target_y
        
        mid_x = (x1 + x2) / 2
        
        self.canvas.create_line(x1, y1, mid_x, y1, fill=color, width=3)
        self.canvas.create_line(mid_x, y1, mid_x, y2, fill=color, width=3)
        self.canvas.create_line(mid_x, y2, x2, y2, fill=color, width=3)

    def draw_node(self, text, pos, state):
        x, y = pos
        color = self.get_color(state)
        self.canvas.create_oval(x-15, y-15, x+15, y+15, fill=color, outline="black")
        self.canvas.create_text(x, y, text=str(int(state)), font=("Arial", 10, "bold"))
        self.canvas.create_text(x, y-25, text=text, font=("Arial", 10))

    def draw_gate(self, type_name, pos, state, is_final=False):
        x, y = pos
        color = "white"
        outline = self.get_color(state) if is_final else "black"
        width = 4 if is_final else 2
        
        # Рисуем коробочку микросхемы
        self.canvas.create_rectangle(x-20, y-20, x+20, y+20, fill=color, outline=outline, width=width)
        self.canvas.create_text(x, y, text=type_name, font=("Arial", 9, "bold"))
        
        # Выходной индикатор
        if is_final:
             self.canvas.create_text(x+40, y, text=str(int(state)), font=("Arial", 16, "bold"), fill=outline)

if __name__ == "__main__":
    root = tk.Tk()
    app = LogicCircuitApp(root)
    root.mainloop()