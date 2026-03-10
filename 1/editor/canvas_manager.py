from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsLineItem, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsPathItem, QMenu
from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import QPen, QColor, QPainter, QPainterPath, QBrush, QAction, QTransform
import config

class EditorScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        # задаем поле для рисования
        self.setSceneRect(0, 0, 3000, 3000)

class EditorView(QGraphicsView):
    # сигналы для общения с главным окном
    item_selected = Signal(object)
    item_created = Signal(str, object) 

    def __init__(self, scene):
        super().__init__(scene)
        # сглаживание линий
        self.setRenderHint(QPainter.Antialiasing)
        # отключаем стандартное перетаскивание холста
        self.setDragMode(QGraphicsView.NoDrag)
        
        # текущие настройки кисти
        self.current_tool = config.TOOL_SELECT
        self.current_color = QColor(config.DEFAULT_COLOR)
        self.current_width = config.DEFAULT_LINE_WIDTH
        self.use_fill = config.DEFAULT_FILL
        self.current_layer_id = None
        
        # переменные для процесса рисования
        self.temp_item = None
        self.start_pos = QPointF()
        self.shift_pressed = False
        self.current_path = None
        self.clipboard_data = None

    def set_tool(self, tool):
        self.current_tool = tool
        if tool == config.TOOL_SELECT:
            # включаем рамку выделения (+- bug - на слоях)
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.setCursor(Qt.ArrowCursor)
            # разрешаем трогать объекты
            self._set_items_interactive(True)
        else:
            # режим рисования
            self.setDragMode(QGraphicsView.NoDrag)
            self.setCursor(Qt.CrossCursor)
            # блокируем объекты
            self._set_items_interactive(False)

    def _set_items_interactive(self, active):
        # пробегаем по всем и меняем флаги
        for item in self.scene().items():
            item.setFlag(QGraphicsItem.ItemIsSelectable, active)
            item.setFlag(QGraphicsItem.ItemIsMovable, active)

    def mousePressEvent(self, event):
        # клик лкм
        if event.button() == Qt.LeftButton and self.current_tool != config.TOOL_SELECT:
            if not self.current_layer_id: return
            # запоминаем где нажали
            self.start_pos = self.mapToScene(event.pos())
            # создаем временную фигуру
            self._start_drawing(self.start_pos)
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # тянем мышь - обновляем фигуру
        if self.temp_item:
            self._update_drawing(self.mapToScene(event.pos()))
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # отпустили мышь - фиксируем фигуру
        if event.button() == Qt.LeftButton and self.temp_item:
            self._finish_drawing()
        else:
            super().mouseReleaseEvent(event)
            # сообщаем кого выделили
            if self.scene().selectedItems():
                self.item_selected.emit(self.scene().selectedItems()[0])

    def keyPressEvent(self, event):
        # ловим шифт для ровных фигур
        if event.key() == Qt.Key_Shift: self.shift_pressed = True
        # горячие клавиши
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_C: self.copy_selection()
            if event.key() == Qt.Key_V: self.paste_selection()
            if event.key() == Qt.Key_D: self.duplicate_selection()
        if event.key() == Qt.Key_Delete: self.delete_selection()
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Shift: self.shift_pressed = False
        super().keyReleaseEvent(event)

    # рисовалка 
    def _get_pen(self):
        # настройка карандаша (контур)
        pen = QPen(self.current_color, self.current_width)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        return pen

    def _get_brush(self):
        # настройка заливки
        if self.use_fill:
            return QBrush(self.current_color)
        return QBrush(Qt.NoBrush)

    def _start_drawing(self, pos):
        pen = self._get_pen()
        brush = self._get_brush()
        
        # создаем нужный класс объекта в зависимости от инструмента
        if self.current_tool == config.TOOL_PEN:
            self.current_path = QPainterPath(pos)
            self.temp_item = QGraphicsPathItem(self.current_path)
            self.temp_item.setPen(pen)
            self.temp_item.setBrush(brush) 
            
        elif self.current_tool == config.TOOL_LINE:
            self.temp_item = QGraphicsLineItem(pos.x(), pos.y(), pos.x(), pos.y())
            self.temp_item.setPen(pen)
            
        elif self.current_tool == config.TOOL_RECT:
            self.temp_item = QGraphicsRectItem(pos.x(), pos.y(), 0, 0)
            self.temp_item.setPen(pen)
            self.temp_item.setBrush(brush)
            
        elif self.current_tool == config.TOOL_OVAL:
            self.temp_item = QGraphicsEllipseItem(pos.x(), pos.y(), 0, 0)
            self.temp_item.setPen(pen)
            self.temp_item.setBrush(brush)

        # добавляем на сцену
        if self.temp_item:
            self.scene().addItem(self.temp_item)
            # запоминаем слой внутри объекта
            self.temp_item.setData(Qt.UserRole, self.current_layer_id)

    def _update_drawing(self, curr_pos):
        # перо просто добавляет линию
        if self.current_tool == config.TOOL_PEN:
            self.current_path.lineTo(curr_pos)
            self.temp_item.setPath(self.current_path)
            return

        x, y = self.start_pos.x(), self.start_pos.y()
        w = curr_pos.x() - x
        h = curr_pos.y() - y
        
        # если зажат шифт - делаем квадрат/круг
        if self.shift_pressed and self.current_tool != config.TOOL_LINE:
            size = min(abs(w), abs(h))
            w = size * (1 if w >= 0 else -1)
            h = size * (1 if h >= 0 else -1)

        # обновляем геометрию фигуры
        if self.current_tool == config.TOOL_LINE:
            self.temp_item.setLine(x, y, curr_pos.x(), curr_pos.y())
        elif self.current_tool in [config.TOOL_RECT, config.TOOL_OVAL]:
            # нормализация координат (без отрецательных чисел)
            rect_x = x if w >= 0 else x + w
            rect_y = y if h >= 0 else y + h
            self.temp_item.setRect(rect_x, rect_y, abs(w), abs(h))

    def _finish_drawing(self):
        # завершаем, делаем объект кликабельным
        if self.temp_item:
            self.temp_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.temp_item.setFlag(QGraphicsItem.ItemIsMovable, True)
            self.item_created.emit(self.current_layer_id, self.temp_item)
            self.temp_item = None
            self.current_path = None

    # операции 
    def delete_selection(self):
        for item in self.scene().selectedItems():
            self.scene().removeItem(item)

    def copy_selection(self):
        items = self.scene().selectedItems()
        if not items: return
        item = items[0]
        # сохраняем свойства объекта в словарь
        self.clipboard_data = {
            "type": type(item),
            "pen": item.pen(),
            "brush": getattr(item, "brush", lambda: QBrush(Qt.NoBrush))(),
            "rect": getattr(item, "rect", lambda: None)(),
            "line": getattr(item, "line", lambda: None)(),
            "path": getattr(item, "path", lambda: None)(),
            "pos": item.pos()
        }

    def paste_selection(self):
        if not self.clipboard_data: return
        data = self.clipboard_data
        
        # восстанавливаем объект из словаря
        new_item = None
        if data["type"] == QGraphicsRectItem: new_item = QGraphicsRectItem(data["rect"])
        elif data["type"] == QGraphicsEllipseItem: new_item = QGraphicsEllipseItem(data["rect"])
        elif data["type"] == QGraphicsLineItem: new_item = QGraphicsLineItem(data["line"])
        elif data["type"] == QGraphicsPathItem: new_item = QGraphicsPathItem(data["path"])
            
        if new_item:
            new_item.setPen(data["pen"])
            if hasattr(new_item, "setBrush"): new_item.setBrush(data["brush"])
            # чуть сдвигаем чтобы было видно
            new_item.setPos(data["pos"] + QPointF(20, 20))
            new_item.setData(Qt.UserRole, self.current_layer_id)
            new_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            new_item.setFlag(QGraphicsItem.ItemIsMovable, True)
            self.scene().addItem(new_item)
            new_item.setSelected(True)
            self.item_created.emit(self.current_layer_id, new_item)

    def duplicate_selection(self):
        self.copy_selection()
        self.paste_selection()