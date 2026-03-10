import tkinter as tk
from logic import TNot, TAnd, TOr

class LogicCircuitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Визуализатор Логической Схемы (XOR)")
        
        self.canvas = tk.Canvas(root, width=650, height=450, bg="white")
        self.canvas.pack(pady=10)
        
        control_frame = tk.Frame(root, bg="#f0f0f0", bd=2, relief=tk.GROOVE)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.var_x = tk.BooleanVar()
        self.var_y = tk.BooleanVar()
        
        tk.Checkbutton(control_frame, text="Вход X (True/False)", variable=self.var_x, 
                       command=self.update_circuit, font=("Arial", 11), bg="#f0f0f0").pack(side=tk.LEFT, padx=20)
        tk.Checkbutton(control_frame, text="Вход Y (True/False)", variable=self.var_y, 
                       command=self.update_circuit, font=("Arial", 11), bg="#f0f0f0").pack(side=tk.LEFT, padx=20)
        
        self.lbl_result = tk.Label(control_frame, text="Результат: 0", font=("Arial", 14, "bold"), fg="blue", bg="#f0f0f0")
        self.lbl_result.pack(side=tk.RIGHT, padx=20)

        self.setup_circuit()
        self.update_circuit()

    def setup_circuit(self):
        self.not_top = TNot("NOT_TOP")
        self.and_top = TAnd("AND_TOP")
        self.not_bottom = TNot("NOT_BOT")
        self.and_bottom = TAnd("AND_BOT")
        self.or_final = TOr("OR_RES")

        self.not_top.link(self.and_top, 2)
        self.and_top.link(self.or_final, 1)
        self.not_bottom.link(self.and_bottom, 1)
        self.and_bottom.link(self.or_final, 2)

        self.pos = {
            "InputX": (60, 100),
            "InputY": (60, 300),
            "NOT_TOP": (180, 250),
            "NOT_BOT": (180, 150),
            "AND_TOP": (350, 100),
            "AND_BOT": (350, 300),
            "OR_RES":  (550, 200)
        }

    def update_circuit(self):
        # Сброс холста
        self.canvas.delete("all")
        
        x_val = self.var_x.get()
        y_val = self.var_y.get()

        self.and_top.In1 = x_val      # X идет в верхний И
        self.not_bottom.In1 = x_val   # X идет в нижний НЕ
        
        self.not_top.In1 = y_val      # Y идет в верхний НЕ
        self.and_bottom.In2 = y_val   # Y идет в нижний И
        
        res = self.or_final.Res
        
        self.lbl_result.config(text=f"Результат: {int(res)}", fg=("green" if res else "red"))

        self.draw_wire(self.pos["InputX"], self.pos["AND_TOP"], x_val, offset_target_y=-10)
        self.draw_wire(self.pos["InputX"], self.pos["NOT_BOT"], x_val)
        
        self.draw_wire(self.pos["InputY"], self.pos["NOT_TOP"], y_val)
        self.draw_wire(self.pos["InputY"], self.pos["AND_BOT"], y_val, offset_target_y=10)

        self.draw_wire(self.pos["NOT_TOP"], self.pos["AND_TOP"], self.not_top.Res, offset_target_y=10)
        self.draw_wire(self.pos["NOT_BOT"], self.pos["AND_BOT"], self.not_bottom.Res, offset_target_y=-10)
        self.draw_wire(self.pos["AND_TOP"], self.pos["OR_RES"], self.and_top.Res, offset_target_y=-10)
        self.draw_wire(self.pos["AND_BOT"], self.pos["OR_RES"], self.and_bottom.Res, offset_target_y=10)

        self.draw_node("Вход X", self.pos["InputX"], x_val)
        self.draw_node("Вход Y", self.pos["InputY"], y_val)
        
        self.draw_gate("NOT", self.pos["NOT_TOP"], self.not_top.Res)
        self.draw_gate("NOT", self.pos["NOT_BOT"], self.not_bottom.Res)
        self.draw_gate("AND", self.pos["AND_TOP"], self.and_top.Res)
        self.draw_gate("AND", self.pos["AND_BOT"], self.and_bottom.Res)
        self.draw_gate("OR",  self.pos["OR_RES"],  self.or_final.Res, is_final=True)

    def get_color(self, state):
        return "#32CD32" if state else "#A9A9A9" 

    def draw_wire(self, start, end, state, offset_target_y=0):
        color = self.get_color(state)
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
        color = "white" # Фон элемента
        outline_color = self.get_color(state) if is_final else "black"
        width = 4 if is_final else 2
        
        self.canvas.create_rectangle(x-22, y-22, x+22, y+22, fill=color, outline=outline_color, width=width)
        self.canvas.create_text(x, y, text=type_name, font=("Arial", 9, "bold"))
        
        if is_final:
             self.canvas.create_text(x+50, y, text=f"= {int(state)}", font=("Arial", 18, "bold"), fill=outline_color)

if __name__ == "__main__":
    root = tk.Tk()
    app = LogicCircuitApp(root)
    root.mainloop()