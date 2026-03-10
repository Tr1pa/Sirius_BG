import sys
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox)

class SegmentVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(200)
        self.p_start, self.p_end = 0, 0
        self.q_start, self.q_end = 0, 0
        self.a_segments = []
        self.has_data = False

    def update_data(self, p, q, a_segs):
        self.p_start, self.p_end = p
        self.q_start, self.q_end = q
        self.a_segments = a_segs
        self.has_data = True
        self.update() 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.fillRect(self.rect(), QColor("#2b2b2b"))
        
        if not self.has_data:
            painter.setPen(QColor("#888888"))
            painter.drawText(self.rect(), Qt.AlignCenter, "Введите отрезки и нажмите 'Рассчитать'")
            return

        w = self.width()
        h = self.height()
        margin = 40

        all_points = [self.p_start, self.p_end, self.q_start, self.q_end]
        for s, e in self.a_segments:
            all_points.extend([s, e])
            
        min_val = min(all_points) - 2
        max_val = max(all_points) + 2
        range_val = max_val - min_val if max_val != min_val else 10

        def map_x(val):
            return margin + (val - min_val) / range_val * (w - 2 * margin)

        axis_y = h / 2 + 20
        painter.setPen(QPen(QColor("white"), 2))
        painter.drawLine(margin, axis_y, w - margin, axis_y)
        
        sorted_points = sorted(list(set(all_points)))
        font = QFont("Arial", 10)
        painter.setFont(font)
        
        for p in sorted_points:
            px = map_x(p)
            painter.setPen(QPen(QColor("white"), 2))
            painter.drawLine(QPointF(px, axis_y - 5), QPointF(px, axis_y + 5))
            painter.drawText(QRectF(px - 20, axis_y + 10, 40, 20), Qt.AlignCenter, str(int(p)))

        p_rect_y = axis_y - 60
        p_x1, p_x2 = map_x(self.p_start), map_x(self.p_end)
        painter.setBrush(QColor(50, 150, 255, 100))
        painter.setPen(QPen(QColor(50, 150, 255), 2))
        painter.drawRect(QRectF(p_x1, p_rect_y, p_x2 - p_x1, 30))
        painter.setPen(QColor(100, 200, 255))
        painter.drawText(QRectF(p_x1, p_rect_y - 20, p_x2 - p_x1, 20), Qt.AlignCenter, "P")

        q_rect_y = axis_y - 30
        q_x1, q_x2 = map_x(self.q_start), map_x(self.q_end)
        painter.setBrush(QColor(50, 255, 100, 100))
        painter.setPen(QPen(QColor(50, 255, 100), 2))
        painter.drawRect(QRectF(q_x1, q_rect_y, q_x2 - q_x1, 30))
        painter.setPen(QColor(100, 255, 150))
        painter.drawText(QRectF(q_x1, q_rect_y - 45, q_x2 - q_x1, 20), Qt.AlignCenter, "Q")

        painter.setBrush(QBrush(QColor(255, 50, 50), Qt.Dense4Pattern))
        painter.setPen(QPen(QColor(255, 50, 50), 3))
        
        for start, end in self.a_segments:
            ax1, ax2 = map_x(start), map_x(end)
            painter.drawLine(QPointF(ax1, axis_y), QPointF(ax2, axis_y))
            painter.drawRect(QRectF(ax1, axis_y - 5, ax2 - ax1, 10))


class SolverWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ЕГЭ №15: Визуализатор Отрезков")
        self.resize(800, 500)
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QLabel { color: #dddddd; font-size: 14px; }
            QLineEdit { 
                background-color: #333; color: white; 
                border: 1px solid #555; padding: 5px; border-radius: 4px; font-size: 14px;
            }
            QPushButton {
                background-color: #0078d7; color: white; 
                border: none; padding: 10px; border-radius: 4px; font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background-color: #008cfa; }
            QPushButton:pressed { background-color: #0063b1; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        input_layout = QHBoxLayout()
        
        v_p = QVBoxLayout()
        v_p.addWidget(QLabel("Отрезок P (через пробел, напр. 10 20):"))
        self.inp_p = QLineEdit("10 29")
        v_p.addWidget(self.inp_p)
        input_layout.addLayout(v_p)

        v_q = QVBoxLayout()
        v_q.addWidget(QLabel("Отрезок Q (через пробел, напр. 15 30):"))
        self.inp_q = QLineEdit("13 18")
        v_q.addWidget(self.inp_q)
        input_layout.addLayout(v_q)

        layout.addLayout(input_layout)

        self.btn_calc = QPushButton("Найти A и Визуализировать")
        self.btn_calc.clicked.connect(self.calculate)
        layout.addWidget(self.btn_calc)

        # Описание задачи
        self.lbl_task = QLabel("Задача: Найти A, чтобы ((x ∈ A) → (x ∈ P)) ∨ (x ∈ Q) было ложно... \n"
                               "Ищут A = P \\ Q (то, что есть в P, но нет в Q).")
        self.lbl_task.setStyleSheet("color: #aaa; font-style: italic;")
        layout.addWidget(self.lbl_task)

        self.visualizer = SegmentVisualizer()
        layout.addWidget(self.visualizer, 1)

        self.lbl_res = QLabel("Результат A: ...")
        self.lbl_res.setStyleSheet("font-size: 18px; color: #ff5555; font-weight: bold;")
        self.lbl_res.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_res)

    def calculate(self):
        try:
            p_raw = list(map(int, self.inp_p.text().split()))
            if len(p_raw) != 2: raise ValueError
            p_start, p_end = sorted(p_raw)

            q_raw = list(map(int, self.inp_q.text().split()))
            if len(q_raw) != 2: raise ValueError
            q_start, q_end = sorted(q_raw)
            
            result_segments = []

            if p_end < q_start or p_start > q_end:
                result_segments.append((p_start, p_end))
            else:
                if p_start < q_start:
                    result_segments.append((p_start, q_start))
                if p_end > q_end:
                    result_segments.append((q_end, p_end))


            res_str = " U ".join([f"[{s}, {e}]" for s, e in result_segments]) if result_segments else "Пустое множество"
            self.lbl_res.setText(f"A = P \\ Q = {res_str}")
            
            self.visualizer.update_data((p_start, p_end), (q_start, q_end), result_segments)

        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите два числа через пробел для каждого отрезка!\nПример: 10 20")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SolverWindow()
    window.show()
    sys.exit(app.exec())