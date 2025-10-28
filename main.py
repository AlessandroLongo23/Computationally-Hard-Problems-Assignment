from lib.Reader import Reader
from lib.Problem import Problem
from lib.Assignment import Assignment
from lib.Solver import Solver

reader = Reader()

problem_data = reader.read_from_file('tests/test5.swe')

problem = Problem(problem_data)

problem.preprocess(verbose=True)

print(problem)

solver = Solver(problem.s, problem.t, problem.R)
solution = solver.solve()
if solution is None:
    print("No solution found")
else:
    print("Solution found:")
    problem.evaluate_assignment(solution)

solver.print_stats()