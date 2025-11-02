class Clause:
    def __init__(self, literals):
        self.literals = literals

    # satisfied if exactly one literal is TRUE
    def satisfied(self, assignment):
        trues = 0
        for var_id, is_positive in self.literals.items():
            var_value = assignment.get(var_id, False)
            # If the literal is positive (not negated), it's true when var_value is True
            # If the literal is negative (negated), it's true when var_value is False
            literal_satisfied = var_value if is_positive else not var_value
            if literal_satisfied:
                trues += 1

        return trues == 1

    def __str__(self) -> str:
        string = '('
        for key, literal in self.literals.items():
            string += f'{-key if not literal else key},'
        return f"{string[:-1]})"
