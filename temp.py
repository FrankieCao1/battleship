from bauhaus import Encoding, proposition, constraint, Or, And

from bauhaus.utils import count_solutions, likelihood
import string
import random
# import pprint
# pp = pprint.PrettyPrinter(indent=4)

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
    def __init__(self, coords: tuple, length: int, orientation: str):
        self.coords = coords
        self.length = length
        self.orientation = orientation

    def __str__(self):
        boat_coords = ""
        for coord in self.coords:
            boat_coords += (f"({coord[0]},{coord[1]}),")
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
    def __init__(self, coords: tuple, is_hit: bool):
        self.coords = coords
        self.is_hit = is_hit

    def __str__(self):
        return f"Guess({self.coords}, {'Hit' if self.is_hit else 'Miss'})"

@proposition(E)
class Hit(Hashable):
    def __init__(self, coords: tuple):
        self.coords = coords

    def __str__(self):
        return f"Hit({self.coords})"

# ----------------------------------------- Variables -----------------------------------------
board_status = [[' ' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
guesses = []
hits = []
# Mini-Game will have one boat of lengths 5, 4, and 3
all_games = []
# ----------------------------------------- Create all variations -----------------------------------------


def create_coords(length, orientation, board_size):
    boats = []

    if orientation == "vertical":
        for start in range((board_size + 1) - length):
            for r in range(board_size):
                temp_coords = []
                for c in range(length):
                    temp_coords.append((r, c + start))
                coords = tuple(temp_coords)
                boats.append(Boat(coords, length, orientation))

    elif orientation == "horizontal":
        for start in range((board_size + 1) - length):
            for r in range(board_size):
                temp_coords = []
                for c in range(length):
                    temp_coords.append((r, c + start))
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

# Boats by size
all_boats_5 = all_boats_5_horizontal + all_boats_5_vertical
all_boats_4 = all_boats_4_horizontal + all_boats_4_vertical
all_boats_3 = all_boats_3_horizontal + all_boats_3_vertical

# All the boats
all_boats = all_boats_5 + all_boats_4 + all_boats_3

# there is only one boat of length 5,4, and 3 in each game
for boat1 in all_boats_5:
    for boat2 in all_boats_4:
        for boat3 in all_boats_3:
            all_games.append(Game(tuple([boat1, boat2, boat3])))


# ----------------------------------------- Guessing Stuff -----------------------------------------


def get_user_guess(board_status):
    while True:
        try:
            col_input = input("Enter column (A, B, C, etc.): ").upper()
            row_input = input("Enter row (1, 2, 3, etc.): ")

            col = string.ascii_uppercase.index(col_input)
            row = int(row_input) - 1

            if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                if board_status[row][col] in ['H', 'M']:
                    print("Spot already guessed. Please choose another spot.")
                else:
                    return (row, col)  # Return row and column as zero-indexed values
            else:
                print("Invalid input. Please enter a valid coordinate.")
        except (ValueError, IndexError):
            print("Invalid input. Please enter a valid coordinate.")


def process_guess(game_board, player_board, x, y):
    if game_board[x][y] == 1:
        player_board[x][y] = 'H'  # Mark as hit on the player's board
        hits.append((x, y))
        return True
    else:
        player_board[x][y] = 'M'  # Mark as miss on the player's board
        return False

# ----------------------------------------- Generate Random Game -----------------------------------------


BOAT_LENGTHS = [5, 4, 3]  # Lengths of boats to be placed


def is_valid_placement(board, boat_coords):
    for x, y in boat_coords:
        if x < 0 or x >= BOARD_SIZE or y < 0 or y >= BOARD_SIZE or board[x][y] == 1:
            return False
        # Check surrounding cells
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                adj_x, adj_y = x + dx, y + dy
                if 0 <= adj_x < BOARD_SIZE and 0 <= adj_y < BOARD_SIZE and board[adj_x][adj_y] == 1:
                    return False
    return True


def place_boat(board, length, max_attempts=1000):
    attempts = 0
    while attempts < max_attempts:
        orientation = random.choice(['horizontal', 'vertical'])
        if orientation == 'horizontal':
            x = random.randint(0, BOARD_SIZE - 1)
            y = random.randint(0, BOARD_SIZE - length)
            boat_coords = [(x, y + i) for i in range(length)]
        else:
            x = random.randint(0, BOARD_SIZE - length)
            y = random.randint(0, BOARD_SIZE - 1)
            boat_coords = [(x + i, y) for i in range(length)]

        if is_valid_placement(board, boat_coords):
            for coord in boat_coords:
                board[coord[0]][coord[1]] = 1  # Mark the boat position
            return True
        attempts += 1

    return False  # Failed to place the boat


def generate_game():
    board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    for length in BOAT_LENGTHS:
        if not place_boat(board, length):
            # Could not place a boat, so start over or handle it differently
            return generate_game()  # This is a simple recursive approach to start over
    return board
# ----------------------------------------- Frequency Map Stuff -----------------------------------------


def is_valid_game(game):
    # check each boat pair for separation and add constraints based on if it is a valid game or not
    for i in range(len(game.boats)):
        for j in range(i + 1, len(game.boats)):
            boat1 = game.boats[i]
            boat2 = game.boats[j]
            # Check if boats are separated
            if not boats_are_separated(boat1, boat2):
                return False

    return True


def boats_are_separated(boat1, boat2):
    for x1, y1 in boat1.coords:
        for x2, y2 in boat2.coords:
            if abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1:
                return False
    return True


def count_boat_occupancy(solutions):
    occupancy_count = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    try:
        for game, is_valid in solutions.items():
            if hasattr(game, 'boats') and is_valid:
                for boat in game.boats:
                    for x, y in boat.coords:
                        occupancy_count[x][y] += 1
    except AttributeError:
        pass

    return occupancy_count


# ----------------------------------------- Display -----------------------------------------


def print_board(board_status):
    # Print column headers
    print(" ", end=" ")
    for col in range(BOARD_SIZE):
        print(chr(ord('A') + col), end=" ")
    print()

    # Print each row
    for row in range(BOARD_SIZE):
        # Print row number
        print(f"{row + 1}", end=" ")

        # Print each cell in the row
        for col in range(BOARD_SIZE):
            print(board_status[row][col], end=" ")
        print()
# ----------------------------------------- Main -----------------------------------------

def build_theory():
    E._custom_constraints.clear()
    for game in all_games:
        valid_game = True

        # Check each pair of boats in a game for separation
        for i in range(len(game.boats)):
            for j in range(i + 1, len(game.boats)):
                boat1 = game.boats[i]
                boat2 = game.boats[j]
                if not boats_are_separated(boat1, boat2):
                    valid_game = False
                    break
            if not valid_game:
                break

        # If the game is valid, add it as a constraint
        if valid_game:
            E.add_constraint(Game(game.boats))
    
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if (i,j) in hits:
                E.add_constraint(Hit((i,j)))
            else:
                E.add_constraint(~Hit((i,j)))
        
    # for boat in game.boats:
    #     this_coords = []
    #     for coord in hits:
    #         this_coords.append(Hit(coord))
    #     E.add_constraint(And(hits) >> ~boat)
    
    return E

if __name__ == "__main__":
    board_status = generate_game()
    print_board(board_status)
    print()

    player_board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    game_over = False
    while not game_over:
        # Recompile the theory with the updated constraints
        T = build_theory()
        T_new = T.compile()
        new_solution = T_new.solve()

        # Count boat occupancy based on the solutions
        occupancy_count = count_boat_occupancy(new_solution)
        for row in occupancy_count:
            print(row)

        print_board(player_board)  # Print the current board status

        guess_coord = get_user_guess(player_board)  # Get user guessA
        x, y = guess_coord

        # determine if the guess is a hit or miss
        result = process_guess(board_status, player_board, x, y)
        guesses.append((x, y, result))
        print(guesses)