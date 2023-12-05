from bauhaus import Encoding, proposition, constraint, Or, And
from bauhaus.utils import count_solutions, likelihood
import random
# import pprint
# pp = pprint.PrettyPrinter(indent=4)

import numpy as np 
import seaborn as sn 
import matplotlib.pyplot as plt 


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

BOARD_SIZE = 6
VALID = True
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
    
@proposition(E)
class Game(Hashable):
    def __init__(self, boats:tuple):
        self.boats = boats

    def __str__(self):
        game = ""
        for boat in self.boats:
            game+=(f"({boat}, ")
        game.rstrip(", ")
        game+=")"
        return f"{game}"

@proposition(E)
class Guess(Hashable):
    def __init__(self, coords:tuple):
        self.coords = coords

    def __str__(self):
        return f"{self.coords}"
    
@proposition(E)
class Around(Hashable):
    def __init__(self, boat1:Boat, boat2:Boat):
        self.boat1 = boat1
        self.boat2 = boat2

    def __str__(self):
        return f"({self.boat1} (-) {self.boat2})"

# Create the propositions
def create_coords(length, orientation, board_size):
    boats = []

    if orientation == "vertical":
        for start in range((board_size+1)-length):
            for r in range(board_size):
                temp_coords = []
                for c in range(length):
                    temp_coords.append((r,c+start))
                coords = tuple(temp_coords)
                boats.append(Boat(coords, length, orientation))

    elif orientation == "horizontal":
        for start in range((board_size+1)-length):
            for r in range(board_size):
                temp_coords = []
                for c in range(length):
                    temp_coords.append((r,c+start))
                coords = tuple(temp_coords)
                boats.append(Boat(coords, length, orientation))
    
    return boats

# Boats by size and orientation
all_boats_5_horizontal = create_coords(5, "horizontal", BOARD_SIZE)
all_boats_5_vertical = create_coords(5, "vertical", BOARD_SIZE)
all_boats_4_horizontal = create_coords(4, "horizontal", BOARD_SIZE)
all_boats_4_vertical = create_coords(4, "vertical", BOARD_SIZE)
all_boats_3_horizontal = create_coords(3, "horizontal", BOARD_SIZE)
all_boats_3_vertical = create_coords(3, "vertical", BOARD_SIZE)
# all_boats += create_coords(2, "horizontal", BOARD_SIZE)
# all_boats += create_coords(2, "vertical", BOARD_SIZE)

# Boats by size
all_boats_5 = all_boats_5_horizontal + all_boats_5_vertical
all_boats_4 = all_boats_4_horizontal + all_boats_4_vertical
all_boats_3 = all_boats_3_horizontal + all_boats_3_vertical

# All the boats
all_boats = all_boats_5 + all_boats_4 + all_boats_3

# Mini-Game will have one boat of lengths 5, 4, and 3
all_games = []

# there is only one boat of length 5,4, and 3 in each game
for boat1 in all_boats_5:
    for boat2 in all_boats_4:
        for boat3 in all_boats_3:
            all_games.append(Game(tuple([boat1,boat2,boat3])))

# ----------------------------------------- Propositions ----------------------------------------- 
def build_theory():
    # Define when a boat is around
    for i in range(len(all_boats)):
        boat1 = all_boats[i]
        for j in range(i+1, len(all_boats)):
            boat2 = all_boats[j]
            # look at all the coords in the first board
            if boat1.orientation == "vertical":
                # for every coord in boat1 if any of the following are in boat2:
                # check around first coord (not the bottom side)
                possible = []
                start = boat1.coords[0]
                for i in range(start[0]-1, start[0]+1):
                    for j in range (start[1]-1,start[1]):
                        if 0<=i< BOARD_SIZE and 0<=j<BOARD_SIZE:
                            possible.append((i,j))

                # check left and right of the middle coords
                for coord in boat1.coords[1:-1]:
                    for i in range(coord[0]-1, coord[0]+1):
                        if 0<=i <BOARD_SIZE:
                            possible.append((i,coord[1]))

                # check around last coord (not the top side)
                end = boat1.coords[-1]
                for i in range(end[0]-1, end[0]+1):
                    for j in range (end[1],end[1]+1):
                        if 0<=i< BOARD_SIZE and 0<=j<BOARD_SIZE:
                            possible.append((i,j))

                # once found decalre that they are around and break
                for coord in boat2.coords:
                    if coord in possible:
                        E.add_constraint(Around(boat1,boat2))
                        E.add_constraint(Around(boat2,boat1))
                        break
                


            elif boat1.orientation == "horizontal":
                # for every coord in boat1 if any of the following are in boat2:
                # check around first coord (not the right side)
                possible = []
                start = boat1.coords[0]
                for i in range(start[0]-1, start[0]):
                    for j in range (start[1]-1,start[1]+1):
                        if 0<=i< BOARD_SIZE and 0<=j<BOARD_SIZE:
                            possible.append((i,j))

                # check up and down of the middle coords
                for coord in boat1.coords[1:-1]:
                    for j in range (coord[1]-1,coord[1]+1):
                        if 0<=j<BOARD_SIZE:
                            possible.append((coord[0],j))

                # check around last coord (not the left side)
                end = boat1.coords[-1]
                for i in range(end[0], end[0]+1):
                    for j in range (end[1]-1,end[1]+1):
                        if 0<=i< BOARD_SIZE and 0<=j<BOARD_SIZE:
                            possible.append((i,j))
                
                # once found decalre that they are around and break ... else they are not around
                for coord in boat2.coords:
                    if coord in possible:
                        E.add_constraint(Around(boat1,boat2))
                        break
        

    # add a constraint that a game cannot exist where any of the three boats are around
    for boat1 in all_boats_5:
        for boat2 in all_boats_4:
            for boat3 in all_boats_3:
                # no boats should be around each other
                E.add_constraint(Or([Around(boat1,boat2), Around(boat1,boat3),
                                     Around(boat2,boat1), Around(boat2,boat3),
                                     Around(boat3,boat1), Around(boat3,boat2)]) >> ~Game((boat1,boat2,boat3)))

    # If a boat is destroyed then automatically get rid of the surronding things
    # for boat in all_boats:
    #     # need to fix syntax on Around
    #     E.add_constraint(~boat >> ~Around(boat1,boat1))

    # example_game() # Example game
    
    return E

def print_board(sol, reveal=False):
    # if reveal == true, show boats too (if not hit ofc) ⛵
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            coord = (row,col)
            # itterate through the props and find out what is the state at a given coord
            # if board[row][col] == '1':
            #     print("🟢", end="")
            # if board[row][col] == '2':
            #     print("❌", end="")
            # elif board[row][col] == '3':
            #     print("💥", end="")
            # else:
            #     print("⬛", end="")
        print()

    if reveal:
        ...
        # data = np.random.randint(low=1, 
        #                         high=100, 
        #                         size=(10, 10)) 
        
        # # setting the parameter values 
        # annot = True
        
        # # plotting the heatmap 
        # hm = sn.heatmap(data=data, 
        #                 annot=annot) 
        
        # # displaying the plotted heatmap 
        # plt.show() 

    
# for each coord: (satisfiable)/(total possiblites for that coord), remove non-satisfibale to figure out the probability map
# using that map recommend a value

def generate_guesses(guesses):
    # generate at most n guesses
    coords = []
    for _ in range(guesses):
        x = random.randint(0,BOARD_SIZE)
        y = random.randint(0,BOARD_SIZE)
        coords.append((x,y))
    unique_guesses = set(coords)

    return sorted(unique_guesses)

# Similar to print graph in graph theory example
def play_game(sol):
    score = 0

    # define the possible guesses


    # print game board - (needs to be adjusted)
    print_board(sol)

    # print probability density board - (needs to be adjusted)
    print_board(sol)

    # if game is finished, exist and print score
    print(score)
    
def example_game():
    desired_boats = {
        ((0,0), (0,1), (0,2), (0,3), (0,4)),
        ((2,0), (3,0), (4,0), (5,0)),
        ((5,3), (5,4), (5,5))
    }
    desired_guesses = generate_guesses(20)

    ...
    # E.add_constraint(Game(Boat[desired_boats[0]],Boat[desired_boats[1]],Boat[desired_boats[2]]))
    # for guess in desired_guesses:
    #     E.add_constraint(Guess(guess))

if __name__ == "__main__":

    T = build_theory()
    # Don't compile until you're finished adding all your constraints!
    T = T.compile()
    # play_game(T)
    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    # print("# Solutions: %d" % count_solutions(T))
    # pp.pprint("   Solution: %s" % T.solve())
    satified = T.solve()
    # n = random.randint(0,len(satified))
    
    # possible_games = []
    # for boat1 in all_boats_5:
    #     for boat2 in all_boats_4:
    #         for boat3 in all_boats_3:
    #             if satified[Game(boat1,boat2,boat3)]:
    #                 possible_games.append(Game(boat1,boat2,boat3))
    
    # play_game(possible_games)

    # print("\nVariable likelihoods:")
    # for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
    #     # Ensure that you only send these functions NNF formulas
    #     # Literals are compiled to NNF here
    #     print(" %s: %.2f" % (vn, likelihood(T, v)))
    # print()


"""
    To do list
        - implement guessing mechanics
        - make an example game
        - display
"""