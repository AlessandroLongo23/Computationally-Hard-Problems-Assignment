from lib.Assignment import Assignment

class Problem:
    def __init__(self, problem_data):
        self.k, self.s, self.t, self.R = problem_data

    def preprocess(self, verbose: bool = False):
        if verbose: 
            before_tlen, before_rlen, before_ravglen = self.get_stats()

        self.cleanup_t_strings()
        self.cleanup_R_sets()

        if verbose: 
            after_tlen, after_rlen, after_ravglen = self.get_stats()
        
            t_reduction = (((before_tlen - after_tlen) / before_tlen) * 100)
            rlen_reduction = (((before_rlen - after_rlen) / before_rlen) * 100)
            ravglen_reduction = (((before_ravglen - after_ravglen) / before_ravglen) * 100)

            num_assignments = 1
            for key, values in self.R.items():
                num_assignments *= len(values)

            print(f"t's size reduced by {t_reduction:.2f} %: ({before_tlen} -> {after_tlen})")
            print(f"R size reduced by {rlen_reduction:.2f} %: ({before_rlen} -> {after_rlen})")
            print(f"R average size reduced by {ravglen_reduction:.2f} %: ({before_ravglen:.2f} -> {after_ravglen:.2f})")
            print(f'Number of available assignment combinations: {num_assignments}')

    def get_stats(self):
        tlen = len(self.t)
        rlen = len(self.R)
        ravglen = sum(len(values) for values in self.R.values()) / len(self.R)
        return tlen, rlen, ravglen

    def cleanup_t_strings(self):
        # we can safely remove the strings that are substrings of other strings and duplicates
        cleaned_t = []
        for i, t_i in enumerate(self.t):
            # check if we already have this string (remove duplicates)
            if t_i.strip() in [t.strip() for t in cleaned_t]:
                continue
            
            # check if t_i is a substring of any other string in self.t
            is_substring = False
            for j, t_j in enumerate(self.t):
                if i != j and t_i.strip() in t_j.strip() and t_i.strip() != t_j.strip():
                    is_substring = True
                    break
            
            # if t_i is not a substring of any other string, keep it
            if not is_substring:
                cleaned_t.append(t_i)
        
        self.t = cleaned_t

    def cleanup_R_sets(self):
        # we can safely remove the keys that are not in any of the t_i's
        for key in list(self.R.keys()):
            found = False
            for t_i in self.t:
                if key.strip() in t_i.strip():
                    found = True
                    break
            
            if not found:
                del self.R[key]

        # for each R_i, we can safely remove the elements (words) that are not substrings of the string s
        for key, values in self.R.items():
            self.R[key] = {value for value in values if value in self.s}

    def __str__(self):
        result = f"string: {self.s}\n"

        result += '\nt\'s:\n'
        for i in range(len(self.t)):
            result += f"t_{i+1} = {self.t[i]}\n"

        result += '\nR\'s:\n'
        for key, values in self.R.items():
            result += f"{key} ({len(values)}): {', '.join(sorted(values))}\n"

        return result

    def evaluate_assignment(self, assignment: Assignment) -> bool:
        if not assignment.isValid(self.R):
            return False
        
        # for each t_i
        for t_i in self.t:
            # we replace the R_i assignment
            expanded_t_i = t_i
            for letter, assignment_letter in assignment.assignment.items():
                expanded_t_i = expanded_t_i.replace(letter, assignment_letter)
            
            # and check if the resulting string is a substring of the string s
            index = self.s.find(expanded_t_i)
            if index == -1:
                print(f"{t_i} --> {expanded_t_i} is not a substring of s {self.s}")
                return False
            else:
                print(f"{t_i} --> {expanded_t_i} found at index {index}")
                # try to print s with the match highlighted in green (ANSI)
                try:
                    GREEN = "\033[93m"
                    RESET = "\033[0m"
                    start = index
                    end = index + len(expanded_t_i)
                    highlighted = f"{self.s[:start]}{GREEN}{self.s[start:end]}{RESET}{self.s[end:]}\n"
                    print(highlighted)
                except Exception:
                    # if coloring is not supported, skip
                    pass
        
        # if none of the t_i's are not substrings of the string s, then the assignment is valid
        print("The assignment is a solution!")
        return True