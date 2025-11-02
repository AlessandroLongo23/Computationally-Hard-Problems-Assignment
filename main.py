from lib.Reader import SWEReader, OITReader
from lib.Problem import Problem
from lib.Assignment import Assignment
from lib.Solver import Solver
from lib.Translator import Translator

reader = OITReader()

oit_problem_data = reader.read_from_file('tests/1-in-3/test0.oit')

translator = Translator()
swe_problem_data = translator.to_swe(oit_problem_data)

problem = Problem(swe_problem_data)

problem.preprocess(verbose=True)

print(problem)

solver = Solver(problem.s, problem.t, problem.R)
solution = solver.solve()
if solution is None:
    print("No solution found")
else:
    print("Solution found:")
    problem.evaluate_assignment(solution)
    
    # Translate back to OIT format
    oit_solution = translator.from_swe(solution)
    print("\nOIT variable assignments:")
    for var_id in sorted(oit_solution.keys()):
        value = "1" if oit_solution[var_id] else "0"
        print(f"  u{var_id} = {value}")

solver.print_stats()