import tkinter as tk
from tkinter import ttk

class LayerPanel(tk.Frame):
    def __init__(self, parent, on_layer_change, on_visibility_change):
        super().__init__(parent, width=250, bg="#e0e0e0")
        self.pack_propagate(False)
        
        self.on_layer_change = on_layer_change
        self.on_visibility_change = on_visibility_change
        
        self.layer_counter = 0
        self.layers_data = {}

        tk.Label(self, text="Слои и Объекты", bg="#e0e0e0", font=("Arial", 10, "bold")).pack(pady=5)

        self.tree = ttk.Treeview(self, columns=("visible",), selectmode="browse", height=20)
        self.tree.heading("#0", text="Имя")
        self.tree.column("#0", width=140, anchor="w")
        self.tree.heading("visible", text="👁")
        self.tree.column("visible", width=40, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Button-1>", self.on_click)

        btn_frame = tk.Frame(self, bg="#e0e0e0")
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(btn_frame, text="+ Слой", command=self.add_layer).pack(fill=tk.X)

        self.add_layer()

    def add_layer(self):
        self.layer_counter += 1
        layer_name = f"Слой {self.layer_counter}"
        layer_tag = f"layer_{self.layer_counter}"
        
        self.layers_data[layer_tag] = {"visible": True, "name": layer_name}
        self.tree.insert("", 0, iid=layer_tag, text=layer_name, values=("👁",), open=True)
        self.tree.selection_set(layer_tag)
        self.on_layer_change(layer_tag)

    def add_object_to_layer(self, layer_tag, obj_id, obj_type):
        item_iid = f"obj_{obj_id}"
        name = f"{obj_type} #{obj_id}"
        if self.tree.exists(layer_tag):
            self.tree.insert(layer_tag, "end", iid=item_iid, text=name, values=("",))

    def remove_object(self, obj_id):
        item_iid = f"obj_{obj_id}"
        if self.tree.exists(item_iid):
            self.tree.delete(item_iid)

    def on_select(self, event):
        selected_iid = self.tree.focus()
        if not selected_iid:
            return
        if selected_iid.startswith("layer_"):
            self.on_layer_change(selected_iid)
        else:
            parent_layer = self.tree.parent(selected_iid)
            self.on_layer_change(parent_layer)

    def on_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#1":
                item_iid = self.tree.identify_row(event.y)
                if item_iid.startswith("layer_"):
                    self.toggle_layer_visibility(item_iid)

    def toggle_layer_visibility(self, layer_tag):
        is_visible = self.layers_data[layer_tag]["visible"]
        new_state = not is_visible
        self.layers_data[layer_tag]["visible"] = new_state
        icon = "👁" if new_state else "🚫"
        self.tree.set(layer_tag, "visible", icon)
        self.on_visibility_change(layer_tag, new_state)