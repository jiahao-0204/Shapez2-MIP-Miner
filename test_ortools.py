from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import IntVar
import cv2

# test if import works
def test_import():
    model = cp_model.CpModel()
    x = model.NewIntVar(0, 10, 'x')
    y = model.NewIntVar(0, 10, 'y')
    model.Add(x + y == 10)
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.OPTIMAL or status == cp_model.FEASIBLE
    assert solver.Value(x) + solver.Value(y) == 10
    print("Import test passed.")

if __name__ == "__main__":
    test_import()
    print("All tests passed.")