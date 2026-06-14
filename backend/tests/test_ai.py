"""Tests for the AI move suggestion (expectimax + softmax confidence).

These tests cover:
- the heuristic feature helpers (max tile, corner, merges, smoothness, monotonicity),
- the depth-limited expectimax search (legal-move avoidance, obvious merges),
- the softmax move-probability distribution and the best-move-with-confidence wrapper.
"""

import pytest

from game2048 import ai
from game2048.ai import (
    LOSS_PENALTY,
    WIN_REWARD,
    heuristic_score,
    max_value,
    move_probabilities,
    suggest_move,
    suggest_move_with_probability,
)

Board = list[list[int | None]]


# --------------------------------------------------------------------------- #
# _max_tile
# --------------------------------------------------------------------------- #
def test_max_tile_returns_largest():
    board: Board = [
        [2, 4, None, None],
        [None, 128, 8, None],
        [None, None, 16, None],
        [None, None, None, 32],
    ]
    assert ai._max_tile(board) == 128


def test_max_tile_empty_board_is_zero():
    board: Board = [[None] * 4 for _ in range(4)]
    assert ai._max_tile(board) == 0


# --------------------------------------------------------------------------- #
# _max_tile_in_corner
# --------------------------------------------------------------------------- #
def test_max_tile_in_corner_true():
    board: Board = [
        [128, 4, None, None],
        [2, 8, None, None],
        [None, None, None, None],
        [None, None, None, None],
    ]
    assert ai._max_tile_in_corner(board, ai._max_tile(board)) is True


def test_max_tile_in_corner_false_when_centre():
    board: Board = [
        [2, 4, None, None],
        [None, 128, 8, None],
        [None, None, 16, None],
        [None, None, None, 32],
    ]
    assert ai._max_tile_in_corner(board, ai._max_tile(board)) is False


def test_max_tile_in_corner_empty_board_false():
    board: Board = [[None] * 4 for _ in range(4)]
    assert ai._max_tile_in_corner(board, 0) is False


# --------------------------------------------------------------------------- #
# _count_potential_merges
# --------------------------------------------------------------------------- #
def test_count_potential_merges_none():
    board: Board = [
        [2, 4, 8, 16],
        [4, 8, 16, 32],
        [8, 16, 32, 64],
        [16, 32, 64, 128],
    ]
    assert ai._count_potential_merges(board) == 0


def test_count_potential_merges_horizontal_and_vertical():
    board: Board = [
        [2, 2, None, None],
        [2, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
    ]
    # (0,0)-(0,1) horizontal and (0,0)-(1,0) vertical = 2 merges
    assert ai._count_potential_merges(board) == 2


# --------------------------------------------------------------------------- #
# _smoothness
# --------------------------------------------------------------------------- #
def test_smoothness_uniform_board_is_zero():
    board: Board = [[2] * 4 for _ in range(4)]
    assert ai._smoothness(board) == 0.0


def test_smoothness_rougher_board_is_larger():
    smooth: Board = [
        [2, 2, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
    ]
    rough: Board = [
        [2, 256, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
    ]
    assert ai._smoothness(rough) > ai._smoothness(smooth)


# --------------------------------------------------------------------------- #
# _monotonicity
# --------------------------------------------------------------------------- #
def test_monotonicity_perfectly_ordered_is_zero():
    # Every row and column strictly increases, so the board is fully monotonic.
    board: Board = [
        [2, 4, 8, 16],
        [4, 8, 16, 32],
        [8, 16, 32, 64],
        [16, 32, 64, 128],
    ]
    assert ai._monotonicity(board) == pytest.approx(0.0)


def test_monotonicity_penalises_disorder():
    ordered: Board = [
        [2, 4, 8, 16],
        [4, 8, 16, 32],
        [8, 16, 32, 64],
        [16, 32, 64, 128],
    ]
    scrambled: Board = [
        [2, 64, 8, 128],
        [16, 8, 32, 4],
        [128, 16, 2, 64],
        [4, 32, 16, 8],
    ]
    assert ai._monotonicity(scrambled) < ai._monotonicity(ordered)


# --------------------------------------------------------------------------- #
# heuristic_score
# --------------------------------------------------------------------------- #
def test_heuristic_prefers_more_empty_cells():
    fuller: Board = [
        [2, 4, 8, 16],
        [4, 8, 16, 32],
        [8, 16, 32, 64],
        [16, 32, 64, None],
    ]
    emptier: Board = [
        [2, 4, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
    ]
    assert heuristic_score(emptier) > heuristic_score(fuller)


def test_heuristic_rewards_max_tile_in_corner():
    corner: Board = [
        [128, 8, 4, 2],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
    ]
    centre: Board = [
        [8, 4, 2, None],
        [None, 128, None, None],
        [None, None, None, None],
        [None, None, None, None],
    ]
    assert heuristic_score(corner) > heuristic_score(centre)


# --------------------------------------------------------------------------- #
# max_value terminal states
# --------------------------------------------------------------------------- #
def test_max_value_winning_board_returns_reward():
    board: Board = [
        [2048, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
    ]
    assert max_value(board, depth=3) == WIN_REWARD


def test_max_value_lost_board_returns_penalty():
    # Full board with no equal neighbours: no move changes it.
    board: Board = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 2],
    ]
    assert max_value(board, depth=3) == LOSS_PENALTY


# --------------------------------------------------------------------------- #
# suggest_move
# --------------------------------------------------------------------------- #
def test_suggest_move_obvious_horizontal_merge():
    # Only the bottom row has tiles; merging the pair is the sensible play.
    board: Board = [
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [2, 2, None, None],
    ]
    assert suggest_move(board, depth=2) in {'left', 'right'}


def test_suggest_move_never_returns_illegal_direction():
    # Tiles are flush left, so 'left' is illegal and must never be suggested.
    board: Board = [
        [2, 4, None, None],
        [8, 16, None, None],
        [32, 64, None, None],
        [128, 256, None, None],
    ]
    move = suggest_move(board, depth=2)
    assert move != 'left'
    new_board, _ = ai._MOVES[move](board)
    assert new_board != board  # the chosen move actually changes the board


def test_suggest_move_game_over_returns_empty():
    board: Board = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 2],
    ]
    assert not suggest_move(board, depth=2)


# --------------------------------------------------------------------------- #
# move_probabilities
# --------------------------------------------------------------------------- #
def test_move_probabilities_sum_to_one():
    board: Board = [
        [2, 4, 8, 16],
        [None, 4, 8, 32],
        [2, None, 16, 64],
        [4, 8, 32, 128],
    ]
    probabilities = move_probabilities(board, depth=2)
    assert probabilities  # at least one legal move
    assert sum(probabilities.values()) == pytest.approx(1.0)
    assert all(0.0 <= p <= 1.0 for p in probabilities.values())


def test_move_probabilities_only_legal_moves():
    board: Board = [
        [2, 4, None, None],
        [8, 16, None, None],
        [32, 64, None, None],
        [128, 256, None, None],
    ]
    probabilities = move_probabilities(board, depth=2)
    assert 'left' not in probabilities  # flush left, so 'left' is illegal


def test_move_probabilities_higher_sharpness_sharpens():
    board: Board = [
        [2, 4, 8, 16],
        [None, 4, 8, 32],
        [2, None, 16, 64],
        [4, 8, 32, 128],
    ]
    sharp = move_probabilities(board, depth=2, sharpness=20.0)
    flat = move_probabilities(board, depth=2, sharpness=1.0)
    # A higher sharpness concentrates more weight on the single best move.
    assert max(sharp.values()) >= max(flat.values())


def test_move_probabilities_uniform_when_scores_tie(monkeypatch):
    # When every legal move scores the same, confidence is split evenly.
    monkeypatch.setattr(ai, '_move_scores', lambda board, depth: {'left': 5.0, 'right': 5.0})
    probabilities = move_probabilities([[None]], depth=1)
    assert probabilities == pytest.approx({'left': 0.5, 'right': 0.5})


def test_move_probabilities_single_legal_move_is_certain(monkeypatch):
    # A single legal move carries all the confidence.
    monkeypatch.setattr(ai, '_move_scores', lambda board, depth: {'down': 42.0})
    probabilities = move_probabilities([[None]], depth=1)
    assert probabilities == {'down': 1.0}


def test_move_probabilities_game_over_is_empty():
    board: Board = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 2],
    ]
    assert move_probabilities(board, depth=2) == {}


# --------------------------------------------------------------------------- #
# suggest_move_with_probability
# --------------------------------------------------------------------------- #
def test_suggest_move_with_probability_matches_suggest_move():
    board: Board = [
        [2, 4, 8, 16],
        [None, 4, 8, 32],
        [2, None, 16, 64],
        [4, 8, 32, 128],
    ]
    move, probability = suggest_move_with_probability(board, depth=2)
    assert move == suggest_move(board, depth=2)
    assert 0.0 < probability <= 1.0
    # The reported confidence is the max of the full distribution.
    assert probability == pytest.approx(max(move_probabilities(board, depth=2).values()))


def test_suggest_move_with_probability_game_over():
    board: Board = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 2],
    ]
    assert suggest_move_with_probability(board, depth=2) == ('', 0.0)
