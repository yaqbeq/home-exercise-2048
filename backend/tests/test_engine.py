"""Tests for the core 2048 game engine.

These tests cover the requirements:
- generating an initial board with random 2s,
- moving left / right / up / down with merging,
- placing a new tile after a valid move,
- detecting win (a 2048 tile) and lose (no moves) conditions.
"""

import pytest

from game2048 import config
from game2048.engine import (
    generate_initial_board,
    get_empty_cells,
    has_available_moves,
    has_won,
    merge_row_left,
    move_down,
    move_left,
    move_right,
    move_up,
    place_number,
)


def count_values(board):
    """Returns a mapping of tile value -> count for non-empty cells."""
    counts = {}
    for row in board:
        for cell in row:
            if cell is not None:
                counts[cell] = counts.get(cell, 0) + 1
    return counts


# --------------------------------------------------------------------------- #
# get_empty_cells
# --------------------------------------------------------------------------- #
def test_get_empty_cells_all_empty():
    board: list[list[int | None]] = [[None] * 4 for _ in range(4)]
    assert len(get_empty_cells(board)) == 16


def test_get_empty_cells_none_empty():
    board: list[list[int | None]] = [[2] * 4 for _ in range(4)]
    assert get_empty_cells(board) == []


def test_get_empty_cells_specific_positions():
    board = [
        [2, None, 2, None],
        [None, 2, None, 2],
        [2, None, 2, None],
        [None, 2, None, 2],
    ]
    expected = [
        (0, 1),
        (0, 3),
        (1, 0),
        (1, 2),
        (2, 1),
        (2, 3),
        (3, 0),
        (3, 2),
    ]
    assert get_empty_cells(board) == expected


# --------------------------------------------------------------------------- #
# generate_initial_board
# --------------------------------------------------------------------------- #
def test_generate_initial_board_dimensions():
    board = generate_initial_board()
    assert len(board) == 4
    assert all(len(row) == 4 for row in board)


def test_generate_initial_board_only_twos():
    for _ in range(50):
        board = generate_initial_board()
        values = {cell for row in board for cell in row if cell is not None}
        assert values <= {2}


def test_generate_initial_board_count_within_range():
    for _ in range(50):
        board = generate_initial_board()
        filled = sum(1 for row in board for cell in row if cell is not None)
        assert config.MIN_INITIAL_NUMBERS <= filled <= config.MAX_INITIAL_NUMBERS


def test_generate_initial_board_custom_size():
    board = generate_initial_board(size=5, min_numbers=1, max_numbers=1)
    assert len(board) == 5
    assert all(len(row) == 5 for row in board)
    assert sum(1 for row in board for cell in row if cell is not None) == 1


# --------------------------------------------------------------------------- #
# place_number
# --------------------------------------------------------------------------- #
def test_place_number_fills_single_empty_cell():
    board = [
        [2, 2, 2, 2],
        [2, 2, 2, 2],
        [2, 2, 2, None],
        [2, 2, 2, 2],
    ]
    place_number(board)
    assert board[2][3] in {2, 4}


def test_place_number_no_empty_cells_is_noop():
    board: list[list[int | None]] = [[2] * 4 for _ in range(4)]
    snapshot = [row[:] for row in board]
    place_number(board)
    assert board == snapshot


def test_place_number_chance_of_four_zero_places_two():
    board: list[list[int | None]] = [[None] * 4 for _ in range(4)]
    place_number(board, chance_of_four=0)
    assert count_values(board) == {2: 1}


def test_place_number_chance_of_four_one_places_four():
    board: list[list[int | None]] = [[None] * 4 for _ in range(4)]
    place_number(board, chance_of_four=1)
    assert count_values(board) == {4: 1}


# --------------------------------------------------------------------------- #
# merge_row_left
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    ('row', 'expected_row', 'expected_score'),
    [
        ([None, 8, 2, 2], [8, 4, None, None], 4),
        ([4, 2, None, 2], [4, 4, None, None], 4),
        ([None, None, None, None], [None, None, None, None], 0),
        ([None, None, None, 2], [2, None, None, None], 0),
        ([2, 2, 2, 2], [4, 4, None, None], 8),
        ([4, 4, 4, 4], [8, 8, None, None], 16),
        ([2, 2, 4, None], [4, 4, None, None], 4),
        ([2, None, 2, None], [4, None, None, None], 4),
    ],
)
def test_merge_row_left(row, expected_row, expected_score):
    merged, score = merge_row_left(row)
    assert merged == expected_row
    assert score == expected_score


def test_merge_row_left_no_triple_merge():
    # Three equal tiles must merge only the first pair, leaving the third.
    merged, score = merge_row_left([2, 2, 2, None])
    assert merged == [4, 2, None, None]
    assert score == 4


# --------------------------------------------------------------------------- #
# move_left / move_right / move_up / move_down
# --------------------------------------------------------------------------- #
@pytest.fixture
def sample_board():
    return [
        [None, 8, 2, 2],
        [4, 2, None, 2],
        [None, None, None, None],
        [None, None, None, 2],
    ]


def test_move_left(sample_board):
    new_board, score = move_left(sample_board)
    assert new_board == [
        [8, 4, None, None],
        [4, 4, None, None],
        [None, None, None, None],
        [2, None, None, None],
    ]
    assert score == 8


def test_move_right(sample_board):
    new_board, score = move_right(sample_board)
    assert new_board == [
        [None, None, 8, 4],
        [None, None, 4, 4],
        [None, None, None, None],
        [None, None, None, 2],
    ]
    assert score == 8


def test_move_up(sample_board):
    new_board, score = move_up(sample_board)
    assert new_board == [
        [4, 8, 2, 4],
        [None, 2, None, 2],
        [None, None, None, None],
        [None, None, None, None],
    ]
    assert score == 4


def test_move_down(sample_board):
    new_board, score = move_down(sample_board)
    assert new_board == [
        [None, None, None, None],
        [None, None, None, None],
        [None, 8, None, 2],
        [4, 2, 2, 4],
    ]
    assert score == 4


def test_moves_do_not_mutate_input(sample_board):
    snapshot = [row[:] for row in sample_board]
    move_left(sample_board)
    move_right(sample_board)
    move_up(sample_board)
    move_down(sample_board)
    assert sample_board == snapshot


def test_move_left_no_change_when_already_left():
    board = [
        [2, 4, None, None],
        [8, None, None, None],
        [None, None, None, None],
        [4, 2, None, None],
    ]
    new_board, score = move_left(board)
    assert new_board == board
    assert score == 0


# --------------------------------------------------------------------------- #
# has_available_moves
# --------------------------------------------------------------------------- #
def test_has_available_moves_with_empty_cells():
    board = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, None],
    ]
    assert has_available_moves(board) is True


def test_has_available_moves_full_board_with_merge():
    board: list[list[int | None]] = [
        [2, 2, 4, 8],
        [4, 8, 16, 32],
        [2, 4, 8, 16],
        [32, 64, 128, 256],
    ]
    assert has_available_moves(board) is True


def test_has_available_moves_lose_board():
    board: list[list[int | None]] = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 2],
    ]
    assert has_available_moves(board) is False


# --------------------------------------------------------------------------- #
# has_won
# --------------------------------------------------------------------------- #
def test_has_won_true():
    board = [
        [4, None, None, 2],
        [2048, None, None, None],
        [4, 2, None, None],
        [4, None, None, None],
    ]
    assert has_won(board) is True


def test_has_won_false():
    board = [
        [4, None, None, 2],
        [1024, None, None, None],
        [4, 2, None, None],
        [4, None, None, None],
    ]
    assert has_won(board) is False


def test_has_won_above_win_value():
    board: list[list[int | None]] = [[None] * 4 for _ in range(4)]
    board[0][0] = 4096
    assert has_won(board) is True
