class OneHeapGameSolver:
    def __init__(self, fixed_heap, s_min=1, s_max=2):
        self.fixed_heap = fixed_heap
        self.s_min = s_min
        self.s_max = s_max

    def can_player_win(self, Heap, steps): #steps — это общее количество оставшихся ходов для достижения победы
        if Heap >= self.fixed_heap: return steps%2 == 0 #Если значение Heap становится больше или равно 202, игра заканчивается | Если это произошло при чётном steps (то есть у игрока был чётный номер хода), возвращается True — победа
        if steps == 0: return 0 # Если steps достигает нуля, это означает, что ходы закончились, но победы не удалось достичь (Поражение)
        Strategy = [self.can_player_win(Heap+1, steps-1), self.can_player_win(Heap+4, steps-1), self.can_player_win(Heap*3, steps-1)] #Возможные ходы игрока
        return any(Strategy) if (steps-1) % 2 == 0 else all(Strategy)
    
    def start(self):
        m1 = [s for s in range(self.s_min, self.s_max) if self.can_player_win(s, 2)] #Например, f(s,2) означает, что у текущего игрока есть два хода (включая его текущий ход) до достижения победы
        m2 = [s for s in range(self.s_min, self.s_max) if not self.can_player_win(s, 1) and self.can_player_win(s, 3)] # №20
        m3 = [s for s in range(self.s_min, self.s_max) if not self.can_player_win(s, 2) and self.can_player_win(s, 4)] # №21
        return m1, m2, m3

class TwoHeapGameSolver:
    def __init__(self, fixed_heap, s_min=1, s_max=2):
        self.fixed_heap = fixed_heap
        self.s_min = s_min
        self.s_max = s_max
    
    def can_player_win_1(self, Heap_1, Heap_2, steps, s_max):
            if Heap_1+Heap_2>=s_max: return steps%2==0
            if steps==0: return 0
            Strategy = [self.can_player_win(Heap_1+2, Heap_2, steps-1), 
                        self.can_player_win(Heap_1*2, Heap_2, steps-1), 
                        self.can_player_win(Heap_1, Heap_2+2, steps-1), 
                        self.can_player_win(Heap_1, Heap_2*2, steps-1)]
            return any(Strategy) if (steps-1) % 2 == 0 else any(Strategy) #В 19-ом нужно найти минимальное значение, поэтому any(Strategy)
    # ----------Малое изменение кода под условие задачи-------------
    def can_player_win_2(self, Heap_1, Heap_2, steps):
        if Heap_1+Heap_2>=self.fixed_heap: return steps%2==0
        if steps==0: return 0
        Strategy = [self.can_player_win(Heap_1+2, Heap_2, steps-1), 
                    self.can_player_win(Heap_1*2, Heap_2, steps-1), 
                    self.can_player_win(Heap_1, Heap_2+2, steps-1), 
                    self.can_player_win(Heap_1, Heap_2*2, steps-1)]
        return any(Strategy) if (steps-1) % 2 == 0 else all(Strategy) #Теперь all(Strategy), так как в 20-ом нужно найти наименьшие значения.
    
    def start(self):
        m1 = [s for s in range(self.s_min, self.s_max) if self.can_player_win_1(s, 2, 2)] #19 | Для вывода 1 ответа пользуйтесь min()
        m2 = [s for s in range(self.s_min, self.s_max) if not self.can_player_win_2(s, 2, 1) and self.can_player_win(s, 2, 3)] #20
        m3 = [s for s in range(self.s_min, self.s_max) if not self.can_player_win_2(s, 2, 2) and self.can_player_win(s, 2, 4)] #21
        return m1, m2, m3