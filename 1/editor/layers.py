from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QWidget, QVBoxLayout, QLabel, QAbstractItemView
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

class LayerTree(QTreeWidget):
    """ кастомное дерево чтобы ловить дроп слоев """
    z_order_changed = Signal()

    def __init__(self):
        super().__init__()
        self.setHeaderLabels(["Имя", "👁"])
        self.setColumnWidth(0, 180)
        self.setColumnWidth(1, 40)
        
        # включаем перетаскивание
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

    def dropEvent(self, event):
        # сначала перемещаем
        super().dropEvent(event)
        # потом порядок изменился
        self.z_order_changed.emit()

class LayerPanel(QWidget):
    active_layer_changed = Signal(str)

    def __init__(self, canvas_view):
        super().__init__()
        self.canvas_view = canvas_view
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        
        self.layout.addWidget(QLabel("Слои (Drag&Drop)"))

        # создаем наше дерево
        self.tree = LayerTree()
        self.tree.z_order_changed.connect(self.update_scene_z_order)
        self.tree.itemSelectionChanged.connect(self.on_selection_change)
        self.tree.itemClicked.connect(self.on_item_clicked)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)

        self.layout.addWidget(self.tree)
        
        self.layer_counter = 0
        self.create_layer("Холст")

    def create_layer(self, name=None):
        self.layer_counter += 1
        if not name: name = f"Слой {self.layer_counter}"
        layer_id = f"layer_{self.layer_counter}"
        
        item = QTreeWidgetItem(self.tree)
        item.setText(0, name)
        item.setText(1, "👁")
        item.setData(0, Qt.UserRole, layer_id) # храним id скрытым
        item.setFlags(item.flags() | Qt.ItemIsEditable) # можно переименовать
        
        # вставляем всегда наверх
        self.tree.insertTopLevelItem(0, item)
        self.tree.setCurrentItem(item)
        
        self.update_scene_z_order()
        return layer_id

    def add_object_item(self, layer_id, gfx_item):
        # ищем нужный слой по id
        root = self.tree.invisibleRootItem()
        layer_node = None
        for i in range(root.childCount()):
            item = root.child(i)
            if item.data(0, Qt.UserRole) == layer_id:
                layer_node = item
                break
        
        if layer_node:
            # создаем запись об объекте
            obj_name = f"Obj {type(gfx_item).__name__.replace('QGraphics', '').replace('Item', '')}"
            obj_item = QTreeWidgetItem()
            obj_item.setText(0, obj_name)
            obj_item.setData(0, Qt.UserRole, gfx_item)
            
            # добавляем внутрь папки слоя
            layer_node.insertChild(0, obj_item)
            layer_node.setExpanded(True)
            
            self.update_scene_z_order()

    def update_scene_z_order(self):
        """ пересчет глубины отрисовки """
        root = self.tree.invisibleRootItem()
        total_layers = root.childCount()
        
        # бежим по слоям сверху вниз
        for i in range(total_layers):
            layer_item = root.child(i)
            # чем выше слой в списке, тем больше Z
            base_z = (total_layers - i) * 10000 
            
            # теперь по объектам внутри слоя
            obj_count = layer_item.childCount()
            for j in range(obj_count):
                obj_item = layer_item.child(j)
                gfx_item = obj_item.data(0, Qt.UserRole)
                
                if gfx_item:
                    final_z = base_z + (obj_count - j)
                    gfx_item.setZValue(final_z)

    def on_selection_change(self):
        # кликнули в дерево - ищем что выбрали
        items = self.tree.selectedItems()
        if not items: return
        item = items[0]
        data = item.data(0, Qt.UserRole)
        
        if isinstance(data, str) and data.startswith("layer_"):
            # это слой
            self.active_layer_changed.emit(data)
            self.canvas_view.scene().clearSelection()
        else:
            # это объект
            gfx_item = data
            if gfx_item:
                gfx_item.setSelected(True)
                parent = item.parent()
                if parent:
                    self.active_layer_changed.emit(parent.data(0, Qt.UserRole))

    def on_item_clicked(self, item, column):
        # клик по глазику (bug)
        if column == 1:
            is_visible = item.text(1) == "👁"
            new_state = not is_visible
            item.setText(1, "👁" if new_state else "🚫")
            
            data = item.data(0, Qt.UserRole)
            if isinstance(data, str) and data.startswith("layer_"):
                # прячем все внутри слоя
                count = item.childCount()
                for i in range(count):
                    child = item.child(i)
                    gfx = child.data(0, Qt.UserRole)
                    if gfx: gfx.setVisible(new_state)
            else:
                # прячем конкретный объект
                if data: data.setVisible(new_state)

    def show_context_menu(self, pos):
        # менюшка на пкм
        item = self.tree.itemAt(pos)
        menu = QMenu()
        
        if item is None:
            menu.addAction("Новый слой", lambda: self.create_layer())
        else:
            data = item.data(0, Qt.UserRole)
            if isinstance(data, str) and data.startswith("layer_"):
                menu.addAction("Новый слой", lambda: self.create_layer())
                menu.addAction("Переименовать", lambda: self.tree.editItem(item, 0))
                menu.addSeparator()
                menu.addAction("Удалить слой", lambda: self.delete_layer(item))
            else:
                menu.addAction("Удалить", lambda: self.delete_object(item))
        
        menu.exec(self.tree.mapToGlobal(pos))

    def delete_layer(self, item):
        layer_id = item.data(0, Qt.UserRole)
        scene = self.canvas_view.scene()
        # удаляем графику со сцены
        for i in range(item.childCount()):
            gfx = item.child(i).data(0, Qt.UserRole)
            if gfx: scene.removeItem(gfx)
        # удаляем строку из дерева
        (item.parent() or self.tree.invisibleRootItem()).removeChild(item)

    def delete_object(self, item):
        gfx_item = item.data(0, Qt.UserRole)
        if gfx_item:
            self.canvas_view.scene().removeItem(gfx_item)
        (item.parent() or self.tree.invisibleRootItem()).removeChild(item)