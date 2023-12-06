from bauhaus import Encoding, proposition, constraint, Or, And
from bauhaus.utils import count_solutions, likelihood
import random

import pprint
pp = pprint.PrettyPrinter(indent=4)

# import numpy as np 
# import seaborn as sn 
# import matplotlib.pyplot as plt 


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
class Hit(Hashable):
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
    for boat1 in all_boats:
        for boat2 in all_boats:
            # look at all the coords in the first board
            if boat1.orientation == "vertical":
                # for every coord in boat1 if any of the following are in boat2:
                # check around first coord (not the bottom side)
                possible = []
                start = boat1.coords[0]
                for j in range (start[1]-1,start[1]+2):
                    i = start[0]-1
                    if 0<=i< BOARD_SIZE and 0<=j<BOARD_SIZE:
                        possible.append((i,j))

                # check left and right of the middle coords
                for coord in boat1.coords:
                    for i in range(coord[0]-1, coord[0]+2):
                        if 0<= i <BOARD_SIZE:
                            possible.append((i,coord[1]))

                # check around last coord (not the top side)
                end = boat1.coords[-1]
                for j in range (end[1]-1,end[1]+2):
                    i = end[0]+1
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
                for i in range(start[0]-1, start[0]+2):
                    j = start[1]-1
                    if 0<=i< BOARD_SIZE and 0<=j<BOARD_SIZE:
                        possible.append((i,j))

                # check up and down of the middle coords
                for coord in boat1.coords:
                    for j in range (coord[1]-1,coord[1]+2):
                        if 0<=j<BOARD_SIZE:
                            possible.append((coord[0],j))

                # check around last coord (not the left side)
                end = boat1.coords[-1]
                for i in range(end[0]-1, end[0]+2):
                    j = end[1]+1
                    if 0<=i< BOARD_SIZE and 0<=j<BOARD_SIZE:
                        possible.append((i,j))
                
                # once found decalre that they are around and break ... else they are not around
                for coord in boat2.coords:
                    if coord in possible:
                        E.add_constraint(Around(boat1,boat2))
                        E.add_constraint(Around(boat2,boat1))
                        break
        

    # add a constraint that a game cannot exist where any of the three boats are around
    for boat1 in all_boats_5:
        for boat2 in all_boats_4:
            for boat3 in all_boats_3:
                # no boats should be around each other
                E.add_constraint(Or([Around(boat1,boat2), Around(boat1,boat3),
                                     Around(boat2,boat1), Around(boat2,boat3),
                                     Around(boat3,boat1), Around(boat3,boat2)]) >> ~Game((boat1,boat2,boat3)))
    return E

# ----------------------------------------- End of Propositions ----------------------------------------- 



# ----------------------------------------- Printing Mechanics ----------------------------------------- 
def initialize_board(sol):
    board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    for game in sol:
        for boat in game.boats:
            for coord in boat.coords:
                board[coord[0]][coord[1]]+=1
    return board

def print_board(sol):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            coord = (row,col)           
            if Hit(coord):
                print("💥", end=" ")
            elif Guess(coord):
                print("❌", end=" ")
            else:
                print("⬛", end=" ")
# ----------------------------------------- End of Printing Mechanics ----------------------------------------- 



# ----------------------------------------- Game Mechanics ----------------------------------------- 

# Similar to print graph in graph theory example
def play_game(satisfied, score, game):
    possible_games = []
    for boat1 in all_boats_5:
        for boat2 in all_boats_4:
            for boat3 in all_boats_3:
                if satisfied[Game((boat1,boat2,boat3))]:
                    possible_games.append(Game((boat1,boat2,boat3)))
    possibility_board = initialize_board(possible_games)

    # define the possible guesses
    print("Note: the top left is (0,0)")
    x = int(input("Please enter an x value: "))
    y = int(input("Please enter an y value: "))
    if 0<= x<BOARD_SIZE and 0<= y<BOARD_SIZE:
        # check if that place has already been guessed
        while possibility_board[x][y] == 0:
            x = int(input("Please enter an x value: "))
            y = int(input("Please enter an y value: "))
        # this syntax is definately wrong
        satisfied.add_constraint(Guess((x,y)))
    
    # if there is a boat at the coord >> hit (update sol)
    hit = False
    for boat in game.boats:
        for coord in boat.coords:
            satisfied.add_constraint(Guess(coord) >> Hit(coord))
            hit = True
    
    if not hit:
        for boat1 in all_boats_5:
                for boat2 in all_boats_4:
                    for boat3 in all_boats_3:
                        if (x,y) in boat1.coords or (x,y) in boat2.coords or (x,y) in boat3.coords:
                            satisfied.add_constraint(~Game((boat1,boat2,boat3)))
    
    # check if the boat has been are destroyed (all coords hit)
    for boat in game.boats:
        hits = []
        for coord in boat.coords:
            hits.append(Hit(coord))
        satisfied.add_constraint(And(hits) >> ~Boat(boat.coords))

    # then remove the possiblity of anything around it
    for boat in game.boats:
        if boat1.orientation == "vertical":
            possible = []
            start = boat1.coords[0]
            for j in range (start[1]-1,start[1]+2):
                i = start[0]-1
                if 0<=i< BOARD_SIZE and 0<=j<BOARD_SIZE:
                    possible.append(Guess(i,j))

            # check left and right of the middle coords
            for coord in boat1.coords:
                for i in range(coord[0]-1, coord[0]+2):
                    if 0<= i <BOARD_SIZE:
                        possible.append(Guess(i,coord[1]))

            # check around last coord (not the top side)
            end = boat1.coords[-1]
            for j in range (end[1]-1,end[1]+2):
                i = end[0]+1
                if 0<=i< BOARD_SIZE and 0<=j<BOARD_SIZE:
                    possible.append(Guess(i,j))
            satisfied.add_constraint(~Boat(boat.coords >> And(possible)))

        elif boat1.orientation == "horizontal":
            # for every coord in boat1 if any of the following are in boat2:
            # check around first coord (not the right side)
            possible = []
            start = boat1.coords[0]
            for i in range(start[0]-1, start[0]+2):
                j = start[1]-1
                if 0<=i< BOARD_SIZE and 0<=j<BOARD_SIZE:
                    possible.append(Guess(i,j))

            # check up and down of the middle coords
            for coord in boat1.coords:
                for j in range (coord[1]-1,coord[1]+2):
                    if 0<=j<BOARD_SIZE:
                        possible.append(Guess(coord[0],j))

            # check around last coord (not the left side)
            end = boat1.coords[-1]
            for i in range(end[0]-1, end[0]+2):
                j = end[1]+1
                if 0<=i< BOARD_SIZE and 0<=j<BOARD_SIZE:
                    possible.append(Guess(i,j))
            satisfied.add_constraint(~Boat(boat.coords >> And(possible)))


    satisfied = satisfied.compile().solve()
    temp = []
    for boat1 in all_boats_5:
        for boat2 in all_boats_4:
            for boat3 in all_boats_3:
                if satisfied[Game((boat1,boat2,boat3))]:
                    temp.append(Game((boat1,boat2,boat3)))
    it = initialize_board(temp)
    for line in it:
        for val in line:
            print(val, end="\t ")
        print()

    # print game board
    print_board(game)

    # print probability density board
    # initialize_board(sol)

    # if game is finished, exit and print score
    print("Lower scores are better; your score is: " + score)
    # else play the game but with the added constraint
    # play_game(sol, score+1, game)

def generate_guesses(guesses):
    # generate at most n guesses
    coords = []
    for _ in range(guesses):
        x = random.randint(0,BOARD_SIZE)
        y = random.randint(0,BOARD_SIZE)
        coords.append((x,y))
    unique_guesses = set(coords)

    return sorted(unique_guesses)

# ----------------------------------------- End of Game Mechanics ----------------------------------------- 

# ----------------------------------------- Main ----------------------------------------- 

if __name__ == "__main__":

    T = build_theory()
    T = T.compile()

    print("\nSatisfiable: %s" % T.satisfiable())
    # pp.pprint("   Solution: %s" % T.solve())
    satisfied = T.solve()
    possible_games = []
    for boat1 in all_boats_5:
        for boat2 in all_boats_4:
            for boat3 in all_boats_3:
                if satisfied[Game((boat1,boat2,boat3))]:
                    possible_games.append(Game((boat1,boat2,boat3)))

    # possibility_board = initialize_board(possible_games)
    # for line in possibility_board:
    #     for val in line:
    #         print(val, end="\t ")
    #     print()
    
    # could pick a random game from possible_games **
    game = random.choice(possible_games)
    # or ... example game
    # desired_boats = {
    #     ((0,0), (0,1), (0,2), (0,3), (0,4)),
    #     ((2,0), (3,0), (4,0), (5,0)),
    #     ((5,3), (5,4), (5,5))
    # }
    # game = Game(Boat[desired_boats[0]],Boat[desired_boats[1]],Boat[desired_boats[2]])
    play_game(satisfied, 0, game)
    # print(data)

# ----------------------------------------- End of Main ----------------------------------------- 

"""
    To do list
        - implement guessing mechanics
        - make an example game
        - display
"""