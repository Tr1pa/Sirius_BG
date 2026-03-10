from functools import lru_cache

class OneHeapGameSolver:
    """
    Решатель для игр с одной кучей камней.
    """
    def __init__(self, win_condition, s_min, s_max, moves_str, is_subtractive=False):
        self.win_condition = win_condition
        self.s_min = s_min
        self.s_max = s_max
        self.moves_str = moves_str
        self.moves = self._parse_moves(moves_str)
        self.is_subtractive = is_subtractive

    def _parse_moves(self, moves_str):
        """Парсит строку с ходами в список функций."""
        parsed_moves = []
        for move in moves_str.replace(" ", "").split(','):
            if not move or len(move) < 2: continue
            op = move[0]
            val = int(move[1:])
            if op == '+':
                parsed_moves.append(lambda h, v=val: h + v)
            elif op == '*':
                parsed_moves.append(lambda h, v=val: h * v)
            elif op == '-':
                parsed_moves.append(lambda h, v=val: h - v)
            elif op == '/':
                parsed_moves.append(lambda h, v=val: h // v)
        return parsed_moves

    def get_next_states(self, heap):
        """Получает возможные следующие состояния из текущего."""
        if 'n/k' in self.moves_str:
            states = []
            if heap > 1:
                for k in range(2, heap + 1):
                    if heap % k == 0:
                        states.append(heap + heap // k)
            return states
        
        return [move(heap) for move in self.moves]

    @lru_cache(maxsize=None)
    def can_player_win(self, heap, steps):
        """
        Определяет, может ли текущий игрок (тот, чей сейчас ход) выиграть.
        """
        win_achieved = (heap >= self.win_condition) if not self.is_subtractive else (heap <= self.win_condition)
        if win_achieved:
            return steps % 2 == 0
        if steps == 0:
            return False
        
        next_states = self.get_next_states(heap)
        
        strategy_results = [self.can_player_win(next_heap, steps - 1) for next_heap in next_states]
        
        if (steps % 2) != 0:
            return any(strategy_results)
        else:
            return all(strategy_results)

    def solve(self, task_type):
        """Запускает решение для указанного типа задачи с корректной логикой."""
        self.can_player_win.cache_clear()
        results = []
        for s in range(self.s_min, self.s_max + 1):
            
            #Логика для Задачи 19
            if task_type == '19':
                if self.can_player_win(s, 1):
                    continue

                petya_moves = self.get_next_states(s)
                found_bad_move = False
                for s_prime in petya_moves:
                    if self.can_player_win(s_prime, 1):
                        found_bad_move = True
                        break
                
                if found_bad_move:
                    results.append(s)

            #Логика для Задачи 20
            elif task_type == '20': 
                if not self.can_player_win(s, 1) and self.can_player_win(s, 3):
                    results.append(s)
            
            #Логика для Задачи 21
            elif task_type == '21':
                if not self.can_player_win(s, 2) and self.can_player_win(s, 4):
                    results.append(s)
        return results


class TwoHeapGameSolver:
    """
    Решатель для игр с двумя кучами камней.
    """
    def __init__(self, win_condition, fixed_heap, s_min, s_max, moves_str, is_subtractive=False):
        self.win_condition = win_condition
        self.fixed_heap = fixed_heap
        self.s_min = s_min
        self.s_max = s_max
        self.moves = [move.strip() for move in moves_str.split(',')]
        self.is_subtractive = is_subtractive

    def get_next_states(self, h1, h2):
        """Получает возможные следующие состояния из текущих."""
        next_states = set()
        for move_str in self.moves:
            if not move_str: continue
            
            if 'H1' in move_str and 'H2' in move_str and len(move_str.split()) > 2:
                parts = move_str.split()
                op1, val1 = parts[0][0], int(parts[0][1:])
                op2, val2 = parts[2][0], int(parts[2][1:])
                
                new_h1 = h1 + val1 if op1 == '+' else h1 - val1 if op1 == '-' else h1 * val1 if op1 == '*' else h1 // val1
                new_h2 = h2 + val2 if op2 == '+' else h2 - val2 if op2 == '-' else h2 * val2 if op2 == '*' else h2 // val2
                next_states.add((new_h1, new_h2))
                continue

            parts = move_str.split()
            if len(parts) != 2: continue
            
            op, val = parts[0][0], int(parts[0][1:])
            target = parts[1]

            targets_to_update = []
            if target == 'H1': targets_to_update.append(1)
            elif target == 'H2': targets_to_update.append(2)
            elif target == 'H_any': targets_to_update.extend([1, 2])
            elif target == 'H_smaller':
                if h1 < h2: targets_to_update.append(1)
                elif h2 < h1: targets_to_update.append(2)
                else: targets_to_update.extend([1, 2])
            
            for t in targets_to_update:
                temp_h1, temp_h2 = h1, h2
                value_to_change = temp_h1 if t == 1 else temp_h2
                changed_value = value_to_change + val if op == '+' else value_to_change - val if op == '-' else value_to_change * val if op == '*' else value_to_change // val
                if t == 1:
                    next_states.add((changed_value, temp_h2))
                else:
                    next_states.add((temp_h1, changed_value))
        return list(next_states)

    @lru_cache(maxsize=None)
    def can_player_win(self, h1, h2, steps):
        """
        Определяет, может ли текущий игрок выиграть.
        """
        win_achieved = (h1 + h2 >= self.win_condition) if not self.is_subtractive else (h1 + h2 <= self.win_condition)
        if win_achieved:
            return steps % 2 == 0
        if steps == 0:
            return False

        next_states = self.get_next_states(h1, h2)
        if not next_states: return False
            
        strategy_results = [self.can_player_win(next_h1, next_h2, steps - 1) for next_h1, next_h2 in next_states]

        if (steps % 2) != 0:
            return any(strategy_results)
        else:
            return all(strategy_results)

    def solve(self, task_type):
        self.can_player_win.cache_clear()
        results = []
        for s in range(self.s_min, self.s_max + 1):
            h1, h2 = self.fixed_heap, s

            if task_type == '19':
                if self.can_player_win(h1, h2, 1):
                    continue

                petya_moves = self.get_next_states(h1, h2)
                found_bad_move = False
                for h1_prime, h2_prime in petya_moves:
                    if self.can_player_win(h1_prime, h2_prime, 1):
                        found_bad_move = True
                        break
                
                if found_bad_move:
                    results.append(s)

            elif task_type == '20':
                if not self.can_player_win(h1, h2, 1) and self.can_player_win(h1, h2, 3):
                    results.append(s)

            elif task_type == '21':
                if not self.can_player_win(h1, h2, 2) and self.can_player_win(h1, h2, 4):
                    results.append(s)
        return results