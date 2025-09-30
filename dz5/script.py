import re
from itertools import permutations, product

class TruthTableCalculator:
    def __init__(self):
        self.expression = ""
        self.variables = []
        self.full_table = []

    def _extract_variables(self, expression: str) -> list[str]:
        keywords = {'and', 'or', 'not', 'True', 'False'}
        tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', expression)
        return sorted(list(set(token for token in tokens if token not in keywords)))

    def build_truth_table(self, expression: str) -> list[dict]:
        self.expression = expression
        self.variables = self._extract_variables(expression)
        if not self.variables:
            raise ValueError("В выражении не найдены переменные.")

        self.full_table = []
        num_vars = len(self.variables)
        
        for values_tuple in product([0, 1], repeat=num_vars):
            row = dict(zip(self.variables, values_tuple))
            try:
                result = eval(self.expression, {"__builtins__": {}}, row)
                row['result'] = bool(result)
                self.full_table.append(row)
            except Exception as e:
                raise ValueError(f"Ошибка вычисления выражения: {e}")
        
        return self.full_table

    def generate_expression_from_table(self, table: list[dict]) -> str:
        true_rows = [row for row in table if row['result']]

        if not true_rows:
            return "False"
        if len(true_rows) == len(table):
            return "True"

        dnf_parts = []
        for row in true_rows:
            term = []
            for var in self.variables:
                if row[var]:
                    term.append(var)
                else:
                    term.append(f"not {var}")
            dnf_parts.append(f"({' and '.join(term)})")
        
        return " or ".join(dnf_parts)

    def solve_ege_task(self, expression: str, partial_table: list[dict]) -> list[str]:
        full_table = self.build_truth_table(expression)
        
        if not self.variables or len(self.variables) != 4:
            raise ValueError("Для решения задачи выражение должно содержать 4 уникальные переменные.")

        target_result = partial_table[0]['result']
        candidate_rows = [row for row in full_table if row['result'] == target_result]

        if len(candidate_rows) < len(partial_table):
            return []

        solutions = []
        columns = ['F1', 'F2', 'F3', 'F4']

        for p_vars in permutations(self.variables):
            for p_rows in permutations(candidate_rows, len(partial_table)):
                is_valid_mapping = True
                for i, problem_row in enumerate(partial_table):
                    candidate_row = p_rows[i]
                    for col_idx, col_name in enumerate(columns):
                        var_for_this_col = p_vars[col_idx] 
                        problem_value = problem_row[col_name] 
                        
                        if problem_value is not None and problem_value != candidate_row[var_for_this_col]:
                            is_valid_mapping = False
                            break
                    if not is_valid_mapping:
                        break
                
                if is_valid_mapping:
                    solution = "".join(p_vars)
                    if solution not in solutions:
                        solutions.append(solution)
        
        return solutions