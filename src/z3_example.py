# z3_example.py
# Simple demonstration of Z3 solving constraints.
from z3 import Int, Solver
x, y, z = Int('x'), Int('y'), Int('z')
s = Solver()
s.add(x > 5, x + y == 10, z != 0)
print("Solver check:", s.check())
print("Model found:", s.model())
