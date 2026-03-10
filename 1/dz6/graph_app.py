import tkinter as tk
from config import CONFIG_WINDOW
from graph_data import POINTS, CONFIG
from color_database import COLORS
CONFIG = {**CONFIG_WINDOW, **CONFIG}

class GraphApp(tk.Tk):
    """
    Класс для создания окна с графиком на основе данных
    """
    def __init__(self, points, colors, config):
        super().__init__()

        self.points = points
        self.colors = colors
        self.config = config

        self.title(self.config["window_title"])

        self.canvas = tk.Canvas(
            self,
            width=self.config["canvas_width"],
            height=self.config["canvas_height"],
            bg='white'
        )
        self.canvas.pack()

        # Расчет ключевых координат для удобства
        self.graph_bottom_y = self.config["canvas_height"] - self.config["padding"]
        self.graph_left_x = self.config["padding"]
        self.graph_top_y = self.config["padding"]
        self.graph_right_x = self.config["canvas_width"] - self.config["padding"]

        # Вызов методов для отрисовки в правильном порядке
        self._draw_axes_and_grid()
        self._draw_filled_areas()
        self._draw_graph_lines()

    def _draw_axes_and_grid(self):
        """Рисует оси X и Y, сетку и текстовые метки."""
        
        # Вертикальная ось (Y)
        num_y_lines = self.config["num_y_lines"]
        max_y_value = self.config["max_y_value"]
        
        for i in range(num_y_lines + 1):
            value = (max_y_value / num_y_lines) * i
            y = self.graph_bottom_y - (value * (self.graph_bottom_y - self.graph_top_y) / max_y_value)
            
            self.canvas.create_line(self.graph_left_x, y, self.graph_right_x, y, fill='#E0E0E0', dash=(2, 4))
            self.canvas.create_text(self.graph_left_x - 10, y, text=str(int(value)), anchor='e')

        # Горизонтальная ось (X)
        x_ticks = [p[0] for p in self.points]
        for x_value in x_ticks:
            x = self.graph_left_x + x_value
            self.canvas.create_line(x, self.graph_top_y, x, self.graph_bottom_y, fill='#E0E0E0', dash=(2, 4))
            self.canvas.create_text(x, self.graph_bottom_y + 15, text=str(x_value), anchor='n')

        # Рисуем жирные оси
        self.canvas.create_line(self.graph_left_x, self.graph_top_y, self.graph_left_x, self.graph_bottom_y, fill='black', width=2)
        self.canvas.create_line(self.graph_left_x, self.graph_bottom_y, self.graph_right_x, self.graph_bottom_y, fill='black', width=2)

    def _draw_filled_areas(self):
        """Рисует закрашенные многоугольники под каждым сегментом графика."""
        start_point = (self.graph_left_x, self.graph_bottom_y - self.points[0][1])
        previous_point = start_point

        for i, (px, py) in enumerate(self.points):
            x_canvas = self.graph_left_x + px
            y_canvas = self.graph_bottom_y - py
            
            x1, y1 = previous_point
            x2, y2 = x_canvas, y_canvas

            polygon_points = [x1, y1, x2, y2, x2, self.graph_bottom_y, x1, self.graph_bottom_y]
            fill_color = self.colors[i % len(self.colors)]
            self.canvas.create_polygon(polygon_points, fill=fill_color, outline="")

            previous_point = (x_canvas, y_canvas)

    def _draw_graph_lines(self):
        """Рисует основную линию графика, пунктирные линии и точки-маркеры."""
        start_point = (self.graph_left_x, self.graph_bottom_y - self.points[0][1])
        previous_point = start_point

        for px, py in self.points:
            x_canvas = self.graph_left_x + px
            y_canvas = self.graph_bottom_y - py
            current_point = (x_canvas, y_canvas)
            
            self.canvas.create_line(previous_point, current_point, fill='black', width=2)
            self.canvas.create_line(x_canvas, y_canvas, x_canvas, self.graph_bottom_y, fill='grey', dash=(4, 2))
            self.canvas.create_oval(x_canvas-3, y_canvas-3, x_canvas+3, y_canvas+3, fill='blue', outline='blue')

            previous_point = current_point


if __name__ == "__main__":
    app = GraphApp(POINTS, COLORS, CONFIG)
    app.mainloop()