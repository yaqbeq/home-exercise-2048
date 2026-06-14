"""AI move suggestion using Expectimax algorithm."""

from copy import deepcopy

from game2048.config import CHANCE_OF_FOUR
from game2048.engine import get_empty_cells, has_available_moves
from game2048.utils import _MOVES


def heuristic(board: list[list[int | None]]) -> float:
    return float(len(get_empty_cells(board)))


def max_value(board: list[list[int | None]], depth: int) -> float:
    """Calculate the maximum score for the max node, which simulates the player's move."""
    if not has_available_moves(board):
        return -1
    if depth <= 0:
        return heuristic(board)
    best_score = -1
    for move in _MOVES.values():
        new_board, score_gained = move(board)
        if new_board == board:
            continue
        # going depth on chance value as this is the start of the new "turn" for the game
        score = score_gained + chance_value(new_board, depth - 1)
        best_score = max(best_score, score)
    return best_score


def chance_value(board: list[list[int | None]], depth: int) -> float:
    """Calculate the expected score for the chance node, which simulates the random spawning of new tiles."""
    new_empty_cells = get_empty_cells(board)
    if not new_empty_cells:  # no empty cells, no chance to add new tile, game over
        return -1
    new_cells = {2: 1 - CHANCE_OF_FOUR, 4: CHANCE_OF_FOUR}
    score = 0
    for cell in new_empty_cells:
        for value, probability in new_cells.items():
            new_board_with_spawned_number = [
                row[:] for row in board
            ]  # deep copy of the board, faster than deepcopy for 2D list
            new_board_with_spawned_number[cell[0]][cell[1]] = value
            score += (
                probability
                * max_value(new_board_with_spawned_number, depth - 1)
                / len(new_empty_cells)
            )
    return score


def suggest_move(board: list[list[int | None]], depth: int = 3) -> str:
    """Suggest the best move for the current board state using Expectimax algorithm and take first moves."""
    best_score = -1
    directions = ['left', 'right', 'up', 'down']
    best_move: str = ''
    for direction in directions:
        new_board, score_gained = _MOVES[direction](board)
        if new_board == board:
            continue
        # going depth on chance value as this is the start of the new "turn" for the game
        score = score_gained + chance_value(new_board, depth - 1)
        if score > best_score:
            best_score = score
            best_move = direction
    return best_move


if __name__ == '__main__':

    def pretty_print(board):
        for row in board:
            print('+------+------+------+------+')
            print(
                '|' + '|'.join(f'{cell if cell not in (0, None) else "":^6}' for cell in row) + '|'
            )
        print('+------+------+------+------+')

    board: list[list[int | None]] = [
        [2, 4, 8, 16],
        [None, 4, 8, 32],
        [2, None, 16, 64],
        [4, 8, 32, 128],
    ]
    best_score = -1
    directions = ['left', 'right', 'up', 'down']
    best_move: str = ''
    new_cells = {2: 1 - CHANCE_OF_FOUR, 4: CHANCE_OF_FOUR}
    # we only need to save one direction info, but for many depths
    for direction in directions:
        score = 0
        new_board, score_gained = _MOVES[direction](board)
        if new_board == board:
            print(f'Move {direction} is illegal.')
            continue

        # chance part
        new_empty_cells = get_empty_cells(new_board)
        # similate new boards with 2 or 4 and calculate heurisitc score
        for cell in new_empty_cells:
            for value, probability in new_cells.items():
                new_board_with_value = deepcopy(new_board)
                new_board_with_value[cell[0]][cell[1]] = value
                score += probability * heuristic(new_board_with_value) / len(new_empty_cells)
        if score > best_score:
            best_score = score
            best_move = direction
            new_board_for_best_move = new_board

    print(f'Best move: {best_move.upper()} with heuristic score: {best_score}')
    pretty_print(new_board_for_best_move)
