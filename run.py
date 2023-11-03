from bauhaus import Encoding, proposition, constraint, Or, And
from bauhaus.utils import count_solutions, likelihood

# These two lines make sure a faster SAT solver is used.
from nnf import config
config.sat_backend = "kissat"

# Encoding that will store all of your constraints
E = Encoding()

# To create propositions, create classes for them first, annotated with "@proposition" and the Encoding
@proposition(E)
class BasicPropositions:

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"A.{self.data}"

class Hashable:
    def __hash__(self):
        return hash(str(self))

    def __eq__(self, __value: object) -> bool:
        return hash(self) == hash(__value)

    def __repr__(self):
        return str(self)

# 0 = empty, 1 = ship segment, 2 = attempted hit, 3 = sucessful hit 
board = [[0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0]]

boats = [5,4,3,3,2]

# ----------------------------------------- Propositions ----------------------------------------- 
@proposition(E)
class Boat(Hashable):
    def __init__(self, coords:tuple):
        self.coords = coords

    def __str__(self):
        boat = ""
        for coord in self.coords:
            boat.append(f"({coord[0]},{coord[1]}),")
        boat.rstrip(",")
        return f"{self.boat}"

@proposition(E)
class Attached(Hashable):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x} (-) {self.y})"
    
@proposition(E)
class Length(Hashable):
    def __init__(self, x, y, n):
        self.x = x
        self.y = y
        self.n = n

    def __str__(self) -> str:
        return f"d({self.x}, {self.y}) = {self.n}"
# ----------------------------------------- Propositions ----------------------------------------- 

def build_theory():
    
    # boats can not be placed 

    return E

# def print_board():
#     for row in range(10):
#         for col in range(10):
#             if board[row][col] == '0':
#                 print("⬛")
#             elif board[row][col] == '1':
#                 print("🟢")
#             elif board[row][col] == '2':
#                 print("❌")
#             elif board[row][col] == '3':
#                 print("💥")
#         print()

if __name__ == "__main__":

    T = build_theory()
    # Don't compile until you're finished adding all your constraints!
    T = T.compile()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    # print("\nSatisfiable: %s" % T.satisfiable())
    # print("# Solutions: %d" % count_solutions(T))
    # print("   Solution: %s" % T.solve())

    # print("\nVariable likelihoods:")
    # for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
    #     # Ensure that you only send these functions NNF formulas
    #     # Literals are compiled to NNF here
    #     print(" %s: %.2f" % (vn, likelihood(T, v)))
    # print()
