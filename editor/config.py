import os
import sys

# размеры окна при запуске
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

def resource_path(relative_path):
    try:
        # PyInstaller создает temp папку и хранит путь в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# путь к иконке, должна лежать рядом с файлом запуска
ICON_PATH = "Sirius_BG\editor\icon.ico"

# константы для инструментов
TOOL_SELECT = "select"  # выбор и перемещение
TOOL_PEN = "pen"        # свободное рисование
TOOL_LINE = "line"      # прямая линия
TOOL_RECT = "rect"      # прямоугольник
TOOL_OVAL = "oval"      # овал/круг

# настройки рисования по умолчанию
DEFAULT_COLOR = "#000000"  # черный цвет
DEFAULT_LINE_WIDTH = 2     # толщина линии
DEFAULT_FILL = False       # заливка выключена (bug - не работает)