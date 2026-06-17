"""Tests for the direction-mapping helpers in :mod:`game2048.utils`."""

from game2048 import utils
from game2048.utils import get_valid_moves


def test_moves_cover_all_four_directions():
    assert set(utils._MOVES) == {'left', 'right', 'up', 'down'}


def test_get_valid_moves_returns_only_changing_directions():
    # A full left column of distinct values: only 'right' shifts the tiles
    # ('up'/'down' can't move or merge a packed column of distinct values).
    board = [
        [2, None, None, None],
        [4, None, None, None],
        [8, None, None, None],
        [16, None, None, None],
    ]
    assert get_valid_moves(board) == ['right']


def test_get_valid_moves_empty_when_game_over():
    # A full board with no adjacent equal tiles: nothing can move.
    board = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 2],
    ]
    assert get_valid_moves(board) == []


def test_get_valid_moves_all_directions_when_centered():
    # A single tile in the middle can move in every direction.
    board = [[None] * 4 for _ in range(4)]
    board[1][1] = 2
    assert set(get_valid_moves(board)) == {'left', 'right', 'up', 'down'}
