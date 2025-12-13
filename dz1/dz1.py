import math

class rectangle:
    def __init__(self, length: int, width: int):
        self.lenght = length
        self.width = width

    def Square(self):
        return self.lenght * self.width
    
    def Perimeter(self):
        return 2 * (self.lenght + self.width)
    
    def __str__(self):
        return f'Прямоугольник\n Стороны: {self.lenght} и {self.width}'

class square(rectangle):
    def __init__(self, side: int):
        super().__init__(side, side)

    def __str__(self):
        return f'Квадрат\n Сторона: {self.lenght}'

class circle:
    def __init__(self, radius: int):
        self.radius = radius
    
    def Square(self):
        return math.pi * (self.radius ** 2)
    
    def Perimeter(self):
        return 2 * math.pi * self.radius
    
    def __str__(self):
        return f'Круг\n Радиус: {self.radius}'
    
class triangle:
    def __init__(self, a: int, b: int, c: int):
        if not (a + b > c and a + c > b and b + c > a):
            raise ValueError("Треугольник с такими сторонами не может существовать.")
        self.a = a
        self.b = b
        self.c = c

    def Square(self):
        s = (self.a + self.b + self.c) / 2
        area = math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))
        return area
    
    def Perimeter(self):
        return self.a + self.b + self.c
    
    def __str__(self):
        return f'Треугольник\n Стороны: {self.a}, {self.b}, {self.c}'
    
def create_figure(vertices: int, *params):
    if vertices == 3:
        if len(params) != 3:
            raise ValueError(f"Для треугольника наебходимо 3 стороны: передано {len(params)}")
        return triangle(*params)
    
    elif vertices == 4:
        if len(params) == 1:
            return square(params[0])
        elif len(params) == 2:
            return rectangle(*params)
        else:
            raise ValueError(f"Для фигуры с 4 вершинами нужен 1 параметр или 2: передано {len(params)}.")
        
    elif vertices == 0:
        if len(params) != 1:
            raise ValueError(f"Для круга необходим 1 параметр: передано {len(params)}.")
        return circle(params[0])
    
    else:
        raise ValueError(f"Фигура не поддерживается")
    
if __name__ == '__main__':
    m = [[3, 5, 12, 13], [4, 10], [4, 8, 12], [0, 7]]
    '''
        Ввод: Количество вершин, (то что нужно для расёта фигуры)
    '''

    for i in m:
        n = create_figure(*i)
        print(n)
        print(f'Площадь: {n.Square():.2f}')
        print(f'Периметр: {n.Perimeter():.2f}\n')
