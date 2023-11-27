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


# ----------------------------------------- Propositions ----------------------------------------- 
@proposition(E)
class Boat(Hashable):
    def __init__(self, coords:tuple, length:int, orientation:str):
        self.coords = coords
        self.length = length
        self.orientation = orientation

    def __str__(self):
        boat_coords = ""
        for coord in self.coords:
            boat_coords+=(f"({coord[0]},{coord[1]}),")
        boat_coords.rstrip(",")
        return f"{boat_coords} + {self.length} + {self.orientation}"
    
    def coords(self):
        return self.coords
    
    def length(self):
        return self.length
    
    def orientation(self):
        return self.orientation


# Create the propositions
def create_coords(length, orientation):
    boats = []

    if orientation == "vertical":
        for start in range(11-length):
            for r in range(10):
                temp_coords = []
                for c in range(length):
                    temp_coords.append((r,c+start))
                coords = tuple(temp_coords)
                boats.append(Boat(coords, length, orientation))

    elif orientation == "horizontal":
        for start in range(11-length):
            for r in range(10):
                temp_coords = []
                for c in range(length):
                    temp_coords.append((r,c+start))
                coords = tuple(temp_coords)
                boats.append(Boat(coords, length, orientation))
    
    return boats

all_boats = []
all_boats += create_coords(5, "horizontal")
all_boats += create_coords(5, "vertical")
all_boats += create_coords(4, "horizontal")
all_boats += create_coords(4, "vertical")
all_boats += create_coords(3, "horizontal")
all_boats += create_coords(3, "vertical")
all_boats += create_coords(2, "horizontal")
all_boats += create_coords(2, "vertical")

for boat in all_boats:
    print(boat)
# ----------------------------------------- Propositions ----------------------------------------- 

def build_theory():
    # there is only one boat of length 5,4,2 and two of three (unique)

    # boats can not be placed next to each other 

    # 

    return E

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


"""
Graph Properties Summary
    1. Hashable to distinguish objects
    2. Add propositions (a representation of each property)
    3. Create the graphs with every possible node edge, adjacency, and distance possibility
    4. Force diconnect - function that adds contraint to force it to disconnect
    5. Example_graph - smaller version of the problem with specific params
    6. Build theory - define what is allowed for every proposition (definition of the props)
    7. Solve and print solutions through a print function
"""