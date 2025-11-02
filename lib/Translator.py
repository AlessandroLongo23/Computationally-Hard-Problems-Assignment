class Translator:
    def __init__(self):
        # Store mapping information for reverse translation
        self.var_to_letters = {}
        self.sorted_variables = []

    def to_swe(self, clauses):
        """
        Translate a 1-in-3 SAT problem (list of Clause objects) to SWE problem instance.
        
        The solver only recognizes single uppercase letters (A-Z) as variables.
        We map each variable to a pair of consecutive letters:
        - Variable 1: A (positive), B (negated)
        - Variable 2: C (positive), D (negated)
        - Variable 3: E (positive), F (negated)
        - etc.
        
        Returns: (k, s, t, R) tuple where:
        - k: number of t strings
        - s: target string (#01#10#001#010#100#)
        - t: list of t strings
        - R: dict mapping literal symbols to their possible values ({'0', '1'})
        """
        # String s is fixed: #01#10#001#010#100#
        # These represent: #01# (one true in pair), #10# (one true in pair), 
        # #001#, #010#, #100# (one true in triple)
        s = '#01#10#001#010#100#'
        
        # Collect all unique variables from all clauses
        all_variables = set()
        for clause in clauses:
            for var_id in clause.literals.keys():
                all_variables.add(var_id)
        
        # Sort variables for consistent ordering
        sorted_variables = sorted(all_variables)
        self.sorted_variables = sorted_variables
        
        # Create mapping from variable ID to letter pairs
        # Each variable gets 2 consecutive letters: one for positive, one for negated
        var_to_letters = {}
        letter_idx = 0
        for var_id in sorted_variables:
            pos_letter = chr(ord('A') + letter_idx)
            neg_letter = chr(ord('A') + letter_idx + 1)
            var_to_letters[var_id] = (pos_letter, neg_letter)
            letter_idx += 2
        self.var_to_letters = var_to_letters
        
        # Build the t strings
        t = []
        
        # 1. One #X_iX_i'# for each variable X_i
        # This becomes #AB# for variable 1, #CD# for variable 2, etc.
        for var_id in sorted_variables:
            pos_letter, neg_letter = var_to_letters[var_id]
            t.append(f'#{pos_letter}{neg_letter}#')
        
        # 2. One #X_iX_jX_k# for each clause
        # The literals in the clause determine which letter to use (positive or negated)
        for clause in clauses:
            literal_letters = []
            for var_id, is_positive in sorted(clause.literals.items()):
                pos_letter, neg_letter = var_to_letters[var_id]
                if is_positive:
                    literal_letters.append(pos_letter)
                else:
                    literal_letters.append(neg_letter)
            
            if len(literal_letters) == 3:
                t.append(f'#{literal_letters[0]}{literal_letters[1]}{literal_letters[2]}#')
            else:
                raise ValueError(f"Clause must have exactly 3 literals, got {len(literal_letters)}")
        
        # Build R: for each literal symbol (letter), R contains {'0', '1'}
        R = {}
        for var_id in sorted_variables:
            pos_letter, neg_letter = var_to_letters[var_id]
            R[pos_letter] = {'0', '1'}
            R[neg_letter] = {'0', '1'}
        
        k = len(t)
        
        return (k, s, t, R)
    
    def from_swe(self, swe_assignment):
        """
        Translate a SWE solution back to OIT variable assignments.
        
        Args:
            swe_assignment: Assignment object from the solver (maps letters to '0' or '1')
        
        Returns:
            dict mapping variable IDs to boolean values (True/False)
        """
        if not self.var_to_letters or not self.sorted_variables:
            raise ValueError("Cannot reverse translate: no mapping stored. Call to_swe() first.")
        
        oit_assignment = {}
        
        for var_id in self.sorted_variables:
            pos_letter, neg_letter = self.var_to_letters[var_id]
            
            # Get the assignment values
            pos_value = swe_assignment.assignment.get(pos_letter, '0')
            neg_value = swe_assignment.assignment.get(neg_letter, '0')
            
            # Due to the #AB# constraint, exactly one should be '1'
            # If pos_letter='1', then u_i = True; if pos_letter='0', then u_i = False
            if pos_value == '1':
                oit_assignment[var_id] = True
            elif neg_value == '1':
                oit_assignment[var_id] = False
            else:
                # Fallback: if both are '0' (shouldn't happen with valid solution)
                # or pos_value is '1', default to True
                oit_assignment[var_id] = (pos_value == '1')
        
        return oit_assignment

