from lib.Reader import SWEReader
from lib.Problem import Problem
from lib.Solver import Solver

reader = SWEReader()
swe_problem_data = reader.read_from_stdin()

problem = Problem(swe_problem_data)
problem.preprocess(verbose=False)

solver = Solver(problem.s, problem.t, problem.R)
solution = solver.solve()

if solution is None:
    print("NO")
else:
    for letter in sorted(solution.assignment.keys()):
        print(f"{letter}:{solution.assignment[letter]}")