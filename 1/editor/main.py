import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QToolBar, QColorDialog, 
                               QSpinBox, QCheckBox, QFileDialog, QMessageBox, QDockWidget)
from PySide6.QtGui import QAction, QIcon, QImage, QPainter, QColor, QBrush
from PySide6.QtCore import Qt, QSize

import config
from canvas_manager import EditorScene, EditorView
from layers import LayerPanel

class VectorEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Vector Editor")
        self.resize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        
        # ставим иконку если файл существует
        if os.path.exists(config.ICON_PATH):
            self.setWindowIcon(QIcon(config.ICON_PATH))

        self._init_ui()

    def _init_ui(self):
        # собираем сцену
        self.scene = EditorScene()
        self.view = EditorView(self.scene)
        self.setCentralWidget(self.view)

        # панель слоев справа
        self.layers_dock = QDockWidget("Слои", self)
        self.layers_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.layer_panel = LayerPanel(self.view)
        self.layers_dock.setWidget(self.layer_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, self.layers_dock)

        # тулбар сверху
        self.toolbar = QToolBar("Tools")
        self.toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(self.toolbar)

        # кнопки инструментов
        self._add_tool_action("Select", config.TOOL_SELECT)
        self._add_tool_action("Pen", config.TOOL_PEN)
        self._add_tool_action("Line", config.TOOL_LINE)
        self._add_tool_action("Rect", config.TOOL_RECT)
        self._add_tool_action("Oval", config.TOOL_OVAL)

        self.toolbar.addSeparator()

        # кнопка сохранения
        save_act = QAction("💾 Save PNG", self)
        save_act.triggered.connect(self.save_image)
        self.toolbar.addAction(save_act)

        self.toolbar.addSeparator()

        # выбор цвета
        self.color_btn = QAction("Color", self)
        self.color_btn.triggered.connect(self.choose_color)
        self.toolbar.addAction(self.color_btn)

        # толщина линии
        self.spin_width = QSpinBox()
        self.spin_width.setRange(1, 50)
        self.spin_width.setValue(config.DEFAULT_LINE_WIDTH)
        self.spin_width.valueChanged.connect(self.change_width)
        self.toolbar.addWidget(self.spin_width)

        # галочка заливки
        self.check_fill = QCheckBox("Fill")
        self.check_fill.stateChanged.connect(self.toggle_fill)
        self.toolbar.addWidget(self.check_fill)

        # связываем сигналы между панелью и холстом
        self.view.item_created.connect(self.layer_panel.add_object_item)
        self.layer_panel.active_layer_changed.connect(self.set_canvas_layer)
        
        # обновляем интерфейс если кликнули на объект
        self.view.item_selected.connect(self.on_item_selected_update_ui)

        # ставим первый слой активным
        self.view.current_layer_id = "layer_1"

    def _add_tool_action(self, name, mode):
        # вспомогательная функция для добавления кнопки
        action = QAction(name, self)
        action.setCheckable(True)
        action.setData(mode)
        action.triggered.connect(lambda: self.set_tool(action))
        self.toolbar.addAction(action)
        if mode == config.TOOL_SELECT:
            action.setChecked(True)

    def set_tool(self, action):
        # переключалка режимов (радиокнопки)
        for act in self.toolbar.actions():
            if act.isCheckable() and act != action:
                act.setChecked(False)
        action.setChecked(True)
        self.view.set_tool(action.data())

    def set_canvas_layer(self, layer_id):
        self.view.current_layer_id = layer_id

    def choose_color(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.view.current_color = col
            # красим выделенное
            for item in self.scene.selectedItems():
                if hasattr(item, "setPen"):
                    pen = item.pen()
                    pen.setColor(col)
                    item.setPen(pen)
                # если заливка активна, красим и ее
                if hasattr(item, "setBrush") and self.view.use_fill:
                     item.setBrush(col)

    def change_width(self, val):
        self.view.current_width = val
        for item in self.scene.selectedItems():
            if hasattr(item, "setPen"):
                pen = item.pen()
                pen.setWidth(val)
                item.setPen(pen)

    def toggle_fill(self, state):
        filled = (state == Qt.Checked)
        self.view.use_fill = filled
        
        # обновляем выделенное
        for item in self.scene.selectedItems():
            if hasattr(item, "setBrush"):
                if filled:
                    item.setBrush(self.view.current_color)
                else:
                    item.setBrush(Qt.NoBrush)

    def on_item_selected_update_ui(self, item):
        # если выбрали объект - проверяем есть ли у него заливка
        if item and hasattr(item, "brush"):
            brush = item.brush()
            is_filled = brush.style() != Qt.NoBrush
            self.check_fill.blockSignals(True)
            self.check_fill.setChecked(is_filled)
            self.view.use_fill = is_filled
            self.check_fill.blockSignals(False)

    def save_image(self):
        # диалог сохранения
        path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png)")
        if path:
            # рендерим сцену в картинку
            image = QImage(self.scene.sceneRect().size().toSize(), QImage.Format_ARGB32)
            image.fill(Qt.transparent)
            painter = QPainter(image)
            self.scene.render(painter)
            painter.end()
            image.save(path)
            QMessageBox.information(self, "Success", "Image Saved!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VectorEditor()
    window.show()
    sys.exit(app.exec())