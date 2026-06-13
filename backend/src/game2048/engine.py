import random

from game2048.config import (
    BOARD_SIZE,
    CHANCE_OF_FOUR,
    MAX_INITIAL_NUMBERS,
    MIN_INITIAL_NUMBERS,
    WIN_VALUE,
)


def get_empty_cells(board: list[list[int | None]]) -> list[tuple[int, int]]:
    """Determines the location of empty cells on the game board."""
    empty_cells = []
    for row_idx, row in enumerate(board):
        for col_idx, cell in enumerate(row):
            if cell is None:
                empty_cells.append((row_idx, col_idx))
    return empty_cells


def place_number(board: list[list[int | None]], chance_of_four: float = CHANCE_OF_FOUR) -> None:
    """Places a number on a random empty cell on the game board."""
    empty_cells = get_empty_cells(board)
    if not empty_cells:
        return
    row, cell = random.choice(empty_cells)
    board[row][cell] = 4 if random.random() < chance_of_four else 2


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


def merge_row_left(row: list[int | None]) -> tuple[list[int | None], int]:
    """Merges a single row to the left, combining equal adjacent numbers.
    Returns the merged row (same length, padded with None) and the score gained.
    """
    filtered_row = [num for num in row if num is not None]
    combined_row = []
    score_gained = 0
    skip_next = False
    for i in range(len(filtered_row)):
        # if the previous number was combined, skip this one
        if skip_next:
            skip_next = False
            continue
        # combine the current number with the next one if they are the same and it is not the last number in the row
        if i + 1 < len(filtered_row) and filtered_row[i] == filtered_row[i + 1]:
            combined_value = filtered_row[i] * 2
            combined_row.append(combined_value)
            score_gained += combined_value
            skip_next = True
        else:
            combined_row.append(filtered_row[i])
    # fill the rest of the row with None values
    combined_row.extend([None] * (len(row) - len(combined_row)))
    return combined_row, score_gained


def move_left(board: list[list[int | None]]) -> tuple[list[list[int | None]], int]:
    """Moves the game board to the left, combining numbers as needed.
    Returns the new board and the score gained from the move.
    """
    new_board: list[list[int | None]] = []
    score_gained = 0
    for row in board:
        merged_row, row_score = merge_row_left(row)
        new_board.append(merged_row)
        score_gained += row_score
    return new_board, score_gained


def move_right(board: list[list[int | None]]) -> tuple[list[list[int | None]], int]:
    """Moves the game board to the right, combining numbers as needed.
    Returns the new board and the score gained from the move.
    """
    # reverse each row, move left, then reverse again
    reversed_board = [row[::-1] for row in board]
    new_board, score_gained = move_left(reversed_board)
    new_board = [row[::-1] for row in new_board]
    return new_board, score_gained


def move_up(board: list[list[int | None]]) -> tuple[list[list[int | None]], int]:
    """Moves the game board up, combining numbers as needed.
    Returns the new board and the score gained from the move.
    """
    # transpose the board, move left, then transpose again
    transposed_board = [list(row) for row in zip(*board)]
    new_board, score_gained = move_left(transposed_board)
    new_board = [list(row) for row in zip(*new_board)]
    return new_board, score_gained


def move_down(board: list[list[int | None]]) -> tuple[list[list[int | None]], int]:
    """Moves the game board down, combining numbers as needed.
    Returns the new board and the score gained from the move.
    """
    # transpose the board, move right, then transpose again
    transposed_board = [list(row) for row in zip(*board)]
    new_board, score_gained = move_right(transposed_board)
    new_board = [list(row) for row in zip(*new_board)]
    return new_board, score_gained


def has_available_moves(board: list[list[int | None]]) -> bool:
    """Returns True if any move would change the board (i.e. the game can continue)."""
    # cheap check: if there are any empty cells, we can move
    if get_empty_cells(board):
        return True
    # more expensive check: if any move would change the board, we can move
    return any(move(board)[0] != board for move in (move_left, move_right, move_up, move_down))


def has_won(board: list[list[int | None]], win_value: int = WIN_VALUE) -> bool:
    """Returns True if any tile on the board has reached the winning value."""
    return any(cell is not None and cell >= win_value for row in board for cell in row)


class Game:
    def __init__(self):
        self.board = generate_initial_board()
        self.score = 0
        self.game_over = False
        self.win = False

    def move(self, direction: str) -> None:
        if self.game_over:
            return
        if direction == 'left':
            new_board, score_gained = move_left(self.board)
        elif direction == 'right':
            new_board, score_gained = move_right(self.board)
        elif direction == 'up':
            new_board, score_gained = move_up(self.board)
        elif direction == 'down':
            new_board, score_gained = move_down(self.board)
        else:
            raise ValueError('Invalid move direction')
        # check if the move changed the board, if so update the state, place a new number, and check for game over
        if new_board != self.board:
            self.board = new_board
            self.score += score_gained
            place_number(self.board)
            # if any tile reached the winning value, the game is won and over
            if has_won(self.board):
                self.win = True
                self.game_over = True
            # if no moves are available after the move, the game is over
            if not has_available_moves(self.board):
                self.game_over = True
