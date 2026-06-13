import random

BOARD_SIZE = 4
MIN_INITIAL_NUMBERS = 2
MAX_INITIAL_NUMBERS = 8
CHANCE_OF_FOUR = 0.1  # typical for 2048 games


def get_empty_cells(board: list[list[int | None]]) -> list[tuple[int, int]]:
    """Determines the location of empty cells on the game board."""
    empty_cells = []
    for row_idx, row in enumerate(board):
        for col_idx, cell in enumerate(row):
            if cell is None:
                empty_cells.append((row_idx, col_idx))
    return empty_cells


def place_number(board: list[list[int | None]], chance_of_four: float = CHANCE_OF_FOUR) -> bool:
    """Places a number on a random empty cell on the game board.
    Returns True if the number was placed successfully, False if there are no empty cells.
    """
    empty_cells = get_empty_cells(board)
    if not empty_cells:
        return False
    row, cell = random.choice(empty_cells)
    board[row][cell] = 4 if random.random() < chance_of_four else 2
    return True


def generate_initial_board(
    size: int = BOARD_SIZE,
    min_numbers: int = MIN_INITIAL_NUMBERS,
    max_numbers: int = MAX_INITIAL_NUMBERS,
) -> list[list[int | None]]:
    """Generates a game board of the specified size."""
    # generate empty board
    board: list[list[int | None]] = [[None] * size for _ in range(size)]

    # determine how many initial numbers to place
    num_initial_numbers = random.randint(min_numbers, max_numbers)
    # place initial numbers on the board
    for _ in range(num_initial_numbers):
        place_number(board, chance_of_four=0)  # only 2s for initial placement
    return board
