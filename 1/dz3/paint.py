import tkinter as tk
from tkinter import colorchooser

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Рисовалка на Python")
        self.root.geometry("800x600")

        self.brush_color = "black"
        self.eraser_color = "white"
        self.tool = "pen" 
        self.line_width = 2
        
        self.start_x = None
        self.start_y = None
        self.current_shape_id = None

        self.setup_ui()

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def setup_ui(self):
        toolbar = tk.Frame(self.root, bg="#e0e0e0", width=100)
        toolbar.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(toolbar, text="Инструменты:", bg="#e0e0e0", font=("Arial", 10, "bold")).pack(pady=5)
        
        self.btn_pen = tk.Button(toolbar, text="Карандаш", command=lambda: self.set_tool("pen"))
        self.btn_pen.pack(pady=2, fill=tk.X, padx=5)

        self.btn_line = tk.Button(toolbar, text="Линия", command=lambda: self.set_tool("line"))
        self.btn_line.pack(pady=2, fill=tk.X, padx=5)

        self.btn_rect = tk.Button(toolbar, text="Прямоугольник", command=lambda: self.set_tool("rect"))
        self.btn_rect.pack(pady=2, fill=tk.X, padx=5)

        self.btn_oval = tk.Button(toolbar, text="Овал", command=lambda: self.set_tool("oval"))
        self.btn_oval.pack(pady=2, fill=tk.X, padx=5)
        
        self.btn_eraser = tk.Button(toolbar, text="Ластик", command=lambda: self.set_tool("eraser"))
        self.btn_eraser.pack(pady=2, fill=tk.X, padx=5)

        tk.Label(toolbar, text="Настройки:", bg="#e0e0e0", font=("Arial", 10, "bold")).pack(pady=10)

        self.btn_color = tk.Button(toolbar, text="Выбрать цвет", bg="black", fg="white", command=self.choose_color)
        self.btn_color.pack(pady=5, fill=tk.X, padx=5)

        tk.Label(toolbar, text="Толщина:", bg="#e0e0e0").pack()
        self.scale_width = tk.Scale(toolbar, from_=1, to=20, orient=tk.HORIZONTAL, bg="#e0e0e0")
        self.scale_width.set(2)
        self.scale_width.pack(padx=5)

        tk.Button(toolbar, text="Очистить", command=self.clear_canvas, bg="#ffcccc").pack(side=tk.BOTTOM, pady=20, fill=tk.X, padx=5)

        self.canvas = tk.Canvas(self.root, bg="white", cursor="cross")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def set_tool(self, tool):
        self.tool = tool
        print(f"Выбран инструмент: {tool}")

    def choose_color(self):
        color = colorchooser.askcolor(color=self.brush_color)[1]
        if color:
            self.brush_color = color
            self.btn_color.config(bg=color)

    def clear_canvas(self):
        self.canvas.delete("all")

    def on_click(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.line_width = self.scale_width.get()

    def on_drag(self, event):
        if self.tool == "pen":
            self.canvas.create_line(self.start_x, self.start_y, event.x, event.y, 
                                    fill=self.brush_color, width=self.line_width, capstyle=tk.ROUND, smooth=True)
            self.start_x = event.x
            self.start_y = event.y
            
        elif self.tool == "eraser":
            self.canvas.create_line(self.start_x, self.start_y, event.x, event.y, 
                                    fill=self.eraser_color, width=self.line_width * 2, capstyle=tk.ROUND, smooth=True)
            self.start_x = event.x
            self.start_y = event.y

        else:
            if self.current_shape_id:
                self.canvas.delete(self.current_shape_id)
            
            x0, y0 = self.start_x, self.start_y
            x1, y1 = event.x, event.y

            if self.tool == "line":
                self.current_shape_id = self.canvas.create_line(x0, y0, x1, y1, fill=self.brush_color, width=self.line_width)
            elif self.tool == "rect":
                self.current_shape_id = self.canvas.create_rectangle(x0, y0, x1, y1, outline=self.brush_color, width=self.line_width)
            elif self.tool == "oval":
                self.current_shape_id = self.canvas.create_oval(x0, y0, x1, y1, outline=self.brush_color, width=self.line_width)

    def on_release(self, event):
        self.current_shape_id = None
        self.start_x = None
        self.start_y = None

if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()