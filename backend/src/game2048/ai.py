"""AI move suggestion using Expectimax algorithm."""

from game2048.api import _MOVES
from game2048.engine import get_empty_cells


def heuristic(board: list[list[int | None]]) -> int:
    return len(get_empty_cells(board))


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

    for direction in ['left', 'right', 'up', 'down']:
        new_board, score_gained = _MOVES[direction](board)
        if new_board == board:
            print(f'Move {direction} is illegal.')
            continue
        print(f'Move {direction}: score = {heuristic(new_board)}')
        pretty_print(new_board)
