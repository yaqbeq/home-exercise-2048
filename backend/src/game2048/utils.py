from game2048 import engine

_MOVES = {
    'left': engine.move_left,
    'right': engine.move_right,
    'up': engine.move_up,
    'down': engine.move_down,
}


def get_valid_moves(board: list[list[int | None]]) -> list[str]:
    """Return the directions that would actually change the board."""
    return [direction for direction, move in _MOVES.items() if move(board)[0] != board]
