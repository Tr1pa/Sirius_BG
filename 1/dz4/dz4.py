import tkinter as tk
import threading

class points:
    def __init__(self):
        self.INITIAL_COORDS = [
            (50, 50),
            (150, 100),
            (80, 200),
            (250, 150),
            (300, 50),
            (300, 250),
            (50, 250)
        ]
        self.points_data = {}
    
    def create_points(self, canvas):
        for i, (x, y) in enumerate(self.INITIAL_COORDS):
            point_id = i + 1
            
            point_item = canvas.create_oval(
                x - 4, y - 4, x + 4, y + 4, 
                fill="blue", outline="blue", tags="point"
            )
            
            canvas.create_text(x + 15, y, text=str(point_id), font=("Arial", 12)) # текстовая метка
            self.points_data[point_id] = {'coords': (x, y), 'item': point_item} # сохраняем
        
        print("Точки созданы с ID от 1 до", len(self.INITIAL_COORDS))

class line:
    def draw_line_between_points(self, canvas, id1, id2):
        """
        Рисует линию между двумя точками по их ID.
        """
        if id1 in self.points_data and id2 in self.points_data:
            coords1 = self.points_data[id1]['coords']
            coords2 = self.points_data[id2]['coords']
            
            canvas.create_line(coords1, coords2, fill="red", width=2)
            print(f"Нарисована линия между точками {id1} и {id2}.")
        else:
            print("Ошибка: один или оба ID не найдены.")

class logic:
    def console_input_handler(self, canvas):
        print('\nВведите команду для соединения точек (например, "1 + 2") и нажмите Enter.')
        print('Для выхода из программы закройте окно.')
        
        while True:
            try:
                command = input("Команда: ")
                
                if not command:
                    continue

                parts = command.split('+')
                if len(parts) == 2:
                    id1_str = parts[0].strip()
                    id2_str = parts[1].strip()
                    
                    id1 = int(id1_str)
                    id2 = int(id2_str)
                    
                    canvas.after(0, self.draw_line_between_points, canvas, id1, id2)
                else:
                    print("Неверный формат команды. Используйте 'ID + ID', например, '1 + 2'.")

            except ValueError:
                print("Ошибка: ID должны быть числами.")
            except Exception as e:
                break

class App(points, line, logic):
    def __init__(self):
        points.__init__(self)

def main():
    root = tk.Tk()
    root.title("Визуализация точек")
    
    canvas = tk.Canvas(root, width=400, height=300, bg="white")
    canvas.pack(pady=20, padx=20)
    
    app = App()
    
    app.create_points(canvas)
    
    input_thread = threading.Thread(target=app.console_input_handler, args=(canvas,), daemon=True)
    input_thread.start()
    
    root.mainloop()

if __name__ == "__main__":
    main()