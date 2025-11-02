from lib.Clause import Clause

class Reader:
    def __init__(self):
        pass

    def read_from_file(self, file_path):
        pass 

class SWEReader(Reader):
    def __init__(self):
        super()

    def read_from_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # the first line is k
        k: int = int(lines[0])

        # then we have the string s
        s: str = lines[1].strip()

        # then we have k strings t_1, t_2, ..., t_k
        t: list[str] = []
        for i in range(2, k + 2):
            t.append(lines[i].strip())

        # the remaining lines are the R_i's, which are sets to be stored in a dictionary
        R: dict[str, set[str]] = {}
        for i in range(k + 2, len(lines)):
            line = lines[i].strip()
            if line:  # skip empty lines
                key, values = line.split(':')
                R[key] = set(values.split(','))

        # return the results
        return k, s, t, R

    def read_from_stdin(self):
        import sys
        lines = sys.stdin.readlines()

        # the first line is k
        k: int = int(lines[0])

        # then we have the string s
        s: str = lines[1].strip()

        # then we have k strings t_1, t_2, ..., t_k
        t: list[str] = []
        for i in range(2, k + 2):
            t.append(lines[i].strip())

        # the remaining lines are the R_i's, which are sets to be stored in a dictionary
        R: dict[str, set[str]] = {}
        for i in range(k + 2, len(lines)):
            line = lines[i].strip()
            if line:  # skip empty lines
                key, values = line.split(':')
                R[key] = set(values.split(','))

        # return the results
        return k, s, t, R

class OITReader(Reader):
    def __init__(self):
        super()

    def read_from_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # then we have the string s
        s: str = lines[0].strip()
        c = s.split("#")
        clauses = []
        for clause in c:
            ls = clause.split(',')
            literals = {}
            for literal in ls:
                literals[abs(int(literal))] = int(literal) > 0 
            clauses.append(Clause(literals))

        # return the results
        return clauses