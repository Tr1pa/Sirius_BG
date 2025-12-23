import tkinter as tk
import config

class EditorCanvas(tk.Canvas):
    def __init__(self, parent, on_object_created_callback=None, on_object_deleted_callback=None):
        super().__init__(parent, bg=config.CANVAS_BG, cursor="cross")
        
        self.on_object_created = on_object_created_callback
        self.on_object_deleted = on_object_deleted_callback
        
        self.current_tool = config.TOOL_LINE
        self.current_color = config.DEFAULT_COLOR
        self.current_width = config.DEFAULT_LINE_WIDTH
        self.current_layer = None
        self.use_fill = False
        
        self.start_x = None
        self.start_y = None
        self.current_object = None
        self.shift_pressed = False
        
        self.selection_box = None
        
        self.bind("<Button-1>", self.on_mouse_down)
        self.bind("<B1-Motion>", self.on_mouse_drag)
        self.bind("<ButtonRelease-1>", self.on_mouse_up)
        
        self.bind_all("<KeyPress-Shift_L>", self.on_shift_press)
        self.bind_all("<KeyRelease-Shift_L>", self.on_shift_release)
        self.bind_all("<KeyPress-Shift_R>", self.on_shift_press)
        self.bind_all("<KeyRelease-Shift_R>", self.on_shift_release)
        self.bind_all("<Delete>", self.delete_selection)

        self.selected_item = None
        self.drag_data = {"x": 0, "y": 0}

    def on_shift_press(self, event):
        self.shift_pressed = True

    def on_shift_release(self, event):
        self.shift_pressed = False

    def set_tool(self, tool):
        self.current_tool = tool
        self.config(cursor="arrow" if tool == config.TOOL_SELECT else "cross")
        self.clear_selection()

    def set_color(self, color):
        self.current_color = color
        if self.selected_item and self.current_tool == config.TOOL_SELECT:
            type_ = self.type(self.selected_item)
            if type_ == "line":
                self.itemconfigure(self.selected_item, fill=color)
            else:
                self.itemconfigure(self.selected_item, outline=color)

    def set_line_width(self, width):
        self.current_width = width
        if self.selected_item and self.current_tool == config.TOOL_SELECT:
            self.itemconfigure(self.selected_item, width=width)
            self._update_selection_box()

    def set_fill(self, enabled):
        self.use_fill = enabled
        if self.selected_item and self.current_tool == config.TOOL_SELECT:
            type_ = self.type(self.selected_item)
            if type_ != "line":
                color = self.current_color if enabled else ""
                self.itemconfigure(self.selected_item, fill=color)

    def set_layer(self, layer_tag):
        self.current_layer = layer_tag

    def toggle_layer_visibility(self, layer_tag, is_visible):
        state = "normal" if is_visible else "hidden"
        self.itemconfigure(layer_tag, state=state)
        if self.selected_item:
            sel_tags = self.gettags(self.selected_item)
            if layer_tag in sel_tags:
                self.clear_selection()

    def delete_selection(self, event=None):
        if self.current_tool == config.TOOL_SELECT and self.selected_item:
            if self.on_object_deleted:
                self.on_object_deleted(self.selected_item)
            self.delete(self.selected_item)
            self.selected_item = None
            self._clear_selection_box()

    def clear_selection(self):
        self.selected_item = None
        self._clear_selection_box()

    def _update_selection_box(self):
        if self.selection_box:
            self.delete(self.selection_box)
        
        if self.selected_item:
            bbox = self.bbox(self.selected_item)
            if bbox:
                x1, y1, x2, y2 = bbox
                pad = 4
                self.selection_box = self.create_rectangle(
                    x1 - pad, y1 - pad, x2 + pad, y2 + pad,
                    dash=(4, 4), outline="#00aaff", width=1, tags="ui_selection"
                )

    def _clear_selection_box(self):
        if self.selection_box:
            self.delete(self.selection_box)
            self.selection_box = None

    def on_mouse_down(self, event):
        self.focus_set()
        
        if self.current_tool == config.TOOL_SELECT:
            item = self.find_closest(event.x, event.y)
            found = None
            if item:
                tags = self.gettags(item[0])
                if "ui_selection" not in tags:
                    found = item[0]
            
            if found:
                self.selected_item = found
                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y
                self._update_selection_box()
            else:
                self.clear_selection()

        else:
            if not self.current_layer:
                return

            self.start_x = event.x
            self.start_y = event.y
            self.clear_selection()
            
            tags = (self.current_layer, "drawing")
            fill_color = self.current_color if self.use_fill else ""

            if self.current_tool == config.TOOL_PEN:
                self.current_object = self.create_line(
                    event.x, event.y, event.x, event.y,
                    fill=self.current_color, width=self.current_width,
                    capstyle=tk.ROUND, joinstyle=tk.ROUND, tags=tags
                )

            elif self.current_tool == config.TOOL_LINE:
                self.current_object = self.create_line(
                    self.start_x, self.start_y, event.x, event.y, 
                    fill=self.current_color, width=self.current_width, tags=tags
                )
            elif self.current_tool == config.TOOL_RECT:
                self.current_object = self.create_rectangle(
                    self.start_x, self.start_y, event.x, event.y, 
                    outline=self.current_color, fill=fill_color, width=self.current_width, tags=tags
                )
            elif self.current_tool == config.TOOL_OVAL:
                self.current_object = self.create_oval(
                    self.start_x, self.start_y, event.x, event.y, 
                    outline=self.current_color, fill=fill_color, width=self.current_width, tags=tags
                )

    def _get_constrained_coords(self, current_x, current_y):
        if not self.shift_pressed:
            return current_x, current_y
        dx = current_x - self.start_x
        dy = current_y - self.start_y
        size = min(abs(dx), abs(dy))
        new_dx = size * (1 if dx >= 0 else -1)
        new_dy = size * (1 if dy >= 0 else -1)
        return self.start_x + new_dx, self.start_y + new_dy

    def on_mouse_drag(self, event):
        if self.current_tool == config.TOOL_SELECT and self.selected_item:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.move(self.selected_item, dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self._update_selection_box()
            
        elif self.current_object:
            if self.current_tool == config.TOOL_PEN:
                current_coords = self.coords(self.current_object)
                current_coords.extend([event.x, event.y])
                self.coords(self.current_object, *current_coords)
            else:
                end_x, end_y = self._get_constrained_coords(event.x, event.y)
                self.coords(self.current_object, self.start_x, self.start_y, end_x, end_y)

    def on_mouse_up(self, event):
        if self.current_object:
            if self.on_object_created:
                t_type = self.current_tool.capitalize()
                self.on_object_created(self.current_layer, self.current_object, t_type)
        self.current_object = None