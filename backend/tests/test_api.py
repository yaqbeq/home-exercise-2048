"""Tests for the stateless HTTP API in :mod:`game2048.api`.

These cover the endpoint contract the frontend relies on:
- ``/api/new`` returns a valid starting board,
- ``/api/move`` merges tiles, spawns a tile on change, and reports outcomes,
- an illegal move leaves the board unchanged and spawns nothing,
- an invalid direction is rejected by request validation,
- win and game-over conditions are reported correctly.
"""

from fastapi.testclient import TestClient

from game2048 import config
from game2048.main import app

client = TestClient(app)


def count_filled(board):
    """Returns the number of non-empty cells on a board."""
    return sum(1 for row in board for cell in row if cell is not None)


# --------------------------------------------------------------------------- #
# /api/new
# --------------------------------------------------------------------------- #
def test_new_returns_4x4_board():
    response = client.post('/api/new')
    assert response.status_code == 200
    board = response.json()['board']
    assert len(board) == config.BOARD_SIZE
    assert all(len(row) == config.BOARD_SIZE for row in board)


def test_new_board_has_only_twos_within_range():
    board = client.post('/api/new').json()['board']
    values = {cell for row in board for cell in row if cell is not None}
    assert values <= {2}
    assert config.MIN_INITIAL_NUMBERS <= count_filled(board) <= config.MAX_INITIAL_NUMBERS


# --------------------------------------------------------------------------- #
# /api/move
# --------------------------------------------------------------------------- #
def test_move_left_merges_and_spawns_tile():
    board = [
        [None, 8, 2, 2],
        [4, 2, None, 2],
        [None, None, None, None],
        [None, None, None, 2],
    ]
    response = client.post('/api/move', json={'board': board, 'direction': 'left'})
    assert response.status_code == 200
    data = response.json()
    assert data['changed'] is True
    assert data['score_gained'] == 8  # 2+2 merges in rows 0 and 1
    # First three rows collapse to the left as in the spec; a new tile spawns
    # somewhere, so compare the leading, deterministic cells only.
    assert data['board'][0][:2] == [8, 4]
    assert data['board'][1][:2] == [4, 4]


def test_move_that_changes_board_spawns_one_new_tile():
    board = [
        [2, 2, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
    ]
    data = client.post('/api/move', json={'board': board, 'direction': 'left'}).json()
    # One merge (2+2 -> 4) plus one spawned tile => two filled cells.
    assert data['changed'] is True
    assert count_filled(data['board']) == 2


def test_illegal_move_leaves_board_unchanged_and_spawns_nothing():
    board = [
        [2, 4, 2, 4],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
    ]
    data = client.post('/api/move', json={'board': board, 'direction': 'left'}).json()
    assert data['changed'] is False
    assert data['board'] == board
    assert data['score_gained'] == 0


def test_invalid_direction_is_rejected():
    board = [[None] * 4 for _ in range(4)]
    response = client.post('/api/move', json={'board': board, 'direction': 'sideways'})
    assert response.status_code == 422


def test_win_is_reported():
    board = [
        [1024, 1024, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
    ]
    data = client.post('/api/move', json={'board': board, 'direction': 'left'}).json()
    assert data['win'] is True


def test_game_over_is_reported():
    # A full board with no adjacent equal tiles: no move changes it.
    board = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 2],
    ]
    data = client.post('/api/move', json={'board': board, 'direction': 'left'}).json()
    assert data['changed'] is False
    assert data['game_over'] is True


# --------------------------------------------------------------------------- #
# /health
# --------------------------------------------------------------------------- #
def test_health_ok():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
