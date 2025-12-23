import tkinter as tk
from tkinter import colorchooser
import config
from layers import LayerPanel
from canvas_manager import EditorCanvas
import file_utils

class VectorEditorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python Vector Paint Pro")
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.configure(bg=config.BG_COLOR)
        
        self.tool_buttons = {} 
        
        self._setup_ui()

    def _setup_ui(self):
        toolbar = tk.Frame(self, bg="#d0d0d0", height=40)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        save_btn = tk.Button(toolbar, text="Save PNG", bg="#ddffdd", 
                             command=lambda: file_utils.save_canvas_as_png(self.canvas))
        save_btn.pack(side=tk.LEFT, padx=5, pady=5)

        tk.Frame(toolbar, width=2, bg="gray").pack(side=tk.LEFT, fill=tk.Y, padx=5)

        tools = [
            ("Select", config.TOOL_SELECT),
            ("Pen", config.TOOL_PEN),
            ("Line", config.TOOL_LINE),
            ("Rect", config.TOOL_RECT),
            ("Oval", config.TOOL_OVAL)
        ]

        for text, mode in tools:
            btn = tk.Button(toolbar, text=text, 
                            command=lambda m=mode: self.set_active_tool(m))
            btn.pack(side=tk.LEFT, padx=2, pady=5)
            self.tool_buttons[mode] = btn

        tk.Frame(toolbar, width=20, bg="#d0d0d0").pack(side=tk.LEFT)

        tk.Label(toolbar, text="Width:", bg="#d0d0d0").pack(side=tk.LEFT)
        self.width_scale = tk.Scale(toolbar, from_=1, to=20, orient=tk.HORIZONTAL, 
                                    bg="#d0d0d0", length=100, command=self.change_width)
        self.width_scale.set(config.DEFAULT_LINE_WIDTH)
        self.width_scale.pack(side=tk.LEFT, padx=5)

        color_btn = tk.Button(toolbar, text="Color", bg="black", fg="white", command=self.choose_color)
        color_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.color_btn_ref = color_btn

        self.fill_var = tk.BooleanVar(value=False)
        fill_check = tk.Checkbutton(toolbar, text="Fill", variable=self.fill_var, 
                                    bg="#d0d0d0", command=self.toggle_fill)
        fill_check.pack(side=tk.LEFT, padx=5)

        del_btn = tk.Button(toolbar, text="x", bg="#ffdddd", 
                            command=lambda: self.canvas.delete_selection())
        del_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        main_area = tk.Frame(self)
        main_area.pack(fill=tk.BOTH, expand=True)

        self.canvas = EditorCanvas(
            main_area,
            on_object_created_callback=None,
            on_object_deleted_callback=None
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.layer_panel = LayerPanel(
            main_area,
            on_layer_change=self.on_active_layer_change,
            on_visibility_change=self.on_visibility_toggle
        )
        self.layer_panel.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.on_object_created = self.layer_panel.add_object_to_layer
        self.canvas.on_object_deleted = self.layer_panel.remove_object

        self.set_active_tool(config.TOOL_PEN)

    def set_active_tool(self, tool_mode):
        self.canvas.set_tool(tool_mode)
        for mode, btn in self.tool_buttons.items():
            if mode == tool_mode:
                btn.config(bg=config.ACTIVE_TOOL_COLOR, relief=tk.SUNKEN)
            else:
                btn.config(bg="SystemButtonFace", relief=tk.RAISED)

    def toggle_fill(self):
        self.canvas.set_fill(self.fill_var.get())

    def change_width(self, val):
        self.canvas.set_line_width(int(val))

    def on_active_layer_change(self, layer_tag):
        self.canvas.set_layer(layer_tag)

    def on_visibility_toggle(self, layer_tag, is_visible):
        self.canvas.toggle_layer_visibility(layer_tag, is_visible)

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.canvas.set_color(color)
            self.color_btn_ref.config(bg=color)

if __name__ == "__main__":
    app = VectorEditorApp()
    app.mainloop()