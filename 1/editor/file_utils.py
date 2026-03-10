from tkinter import filedialog, messagebox
from PIL import ImageGrab

def save_canvas_as_png(canvas_widget):
    existing_box = canvas_widget.find_withtag("ui_selection")
    for item in existing_box:
        canvas_widget.itemconfigure(item, state="hidden")
        
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png")]
    )
    
    if file_path:
        try:
            canvas_widget.update()
            x = canvas_widget.winfo_rootx()
            y = canvas_widget.winfo_rooty()
            w = canvas_widget.winfo_width()
            h = canvas_widget.winfo_height()
            
            img = ImageGrab.grab(bbox=(x, y, x+w, y+h))
            img.save(file_path)
            messagebox.showinfo("Success", "Saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    # Возвращаем рамку
    for item in existing_box:
        canvas_widget.itemconfigure(item, state="normal")