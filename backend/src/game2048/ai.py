"""AI move suggestion using Expectimax algorithm."""

import math

from game2048.config import CHANCE_OF_FOUR
from game2048.engine import get_empty_cells, has_available_moves, has_won
from game2048.utils import _MOVES

DEPTH_LIMIT = 3  # how many plies (move + spawn) to look ahead; adjust for performance vs. quality

# Softmax temperature used to turn move scores into a confidence distribution.
# Lower values sharpen toward the single best move; higher values flatten the
# distribution. The expectimax scores are large and unitless, so they are
# rescaled (see ``move_probabilities``) before this temperature is applied.
TEMPERATURE = 1.0

# Terminal-state values for the search. Large magnitudes so the AI strongly
# prefers winning lines and avoids losing ones, regardless of accumulated score.
WIN_REWARD = 1_000_000.0
LOSS_PENALTY = -1_000_000.0


# Probabilities of a freshly spawned tile being a 2 or a 4.
SPAWN_PROBABILITIES = {2: 1 - CHANCE_OF_FOUR, 4: CHANCE_OF_FOUR}

# Heuristic weights for non-terminal states. These are tuned to encourage the AI to
# keep the board in a "good" state, rather than just maximizing score. The AI
# will still prioritize winning and avoiding losing, but these weights help it make
# better decisions in the mid-game.
EMPTY_WEIGHT = 1000
MERGE_WEIGHT = 500  # potential merges are good, more opportunities to combine tiles
MAX_TILE_WEIGHT = 1000  # having a high tile is good, closer to winning
CORNER_BONUS = 2000  # having the max tile in a corner is very good, easier to build around
MONOTONICITY_WEIGHT = 100  # boards with monotonic rows/columns are easier to manage
SMOOTHNESS_WEIGHT = 10  # smoother boards are easier to merge


def _max_tile(board: list[list[int | None]]) -> int:
    """Return the largest tile on the board (0 if the board is empty)."""
    return max((cell for row in board for cell in row if cell is not None), default=0)


def _max_tile_in_corner(board: list[list[int | None]], max_tile: int) -> bool:
    """Return True if the largest tile sits in one of the four corners."""
    if max_tile == 0:
        return False
    last = len(board) - 1
    corners = (board[0][0], board[0][last], board[last][0], board[last][last])
    return max_tile in corners


def _count_potential_merges(board: list[list[int | None]]) -> int:
    """Count adjacent equal tiles (horizontally and vertically) that could merge."""
    size = len(board)
    merges = 0
    for row in range(size):
        for col in range(size):
            cell = board[row][col]
            if cell is None:
                continue
            if col + 1 < size and board[row][col + 1] == cell:
                merges += 1
            if row + 1 < size and board[row + 1][col] == cell:
                merges += 1
    return merges


def _smoothness(board: list[list[int | None]]) -> float:
    """Sum of absolute log2 differences between adjacent tiles (higher means rougher)."""
    size = len(board)
    roughness = 0.0
    for row in range(size):
        for col in range(size):
            cell = board[row][col]
            if cell is None:
                continue
            value = math.log2(cell)
            right = board[row][col + 1] if col + 1 < size else None
            if right is not None:
                roughness += abs(value - math.log2(right))
            down = board[row + 1][col] if row + 1 < size else None
            if down is not None:
                roughness += abs(value - math.log2(down))
    return roughness


def _monotonicity(board: list[list[int | None]]) -> float:
    """Reward rows/columns ordered consistently. Returns <= 0; 0 means fully monotonic."""
    size = len(board)

    def log_value(cell: int | None) -> float:
        return math.log2(cell) if cell else 0.0

    increasing_lr = decreasing_lr = 0.0
    increasing_ud = decreasing_ud = 0.0
    for row in range(size):
        for col in range(size - 1):
            current, nxt = log_value(board[row][col]), log_value(board[row][col + 1])
            if current > nxt:
                increasing_lr += nxt - current
            else:
                decreasing_lr += current - nxt
    for col in range(size):
        for row in range(size - 1):
            current, nxt = log_value(board[row][col]), log_value(board[row + 1][col])
            if current > nxt:
                increasing_ud += nxt - current
            else:
                decreasing_ud += current - nxt
    return max(increasing_lr, decreasing_lr) + max(increasing_ud, decreasing_ud)


def heuristic_score(board: list[list[int | None]]) -> float:
    """Estimate how promising a non-terminal board is, as a weighted sum of features."""
    empty_cells = len(get_empty_cells(board))
    merge_score = _count_potential_merges(board)
    max_tile = _max_tile(board)
    max_tile_log = math.log2(max_tile) if max_tile else 0.0
    max_tile_in_corner = _max_tile_in_corner(board, max_tile)
    monotonicity_score = _monotonicity(board)
    smoothness_score = _smoothness(board)

    return (
        EMPTY_WEIGHT * empty_cells
        + MERGE_WEIGHT * merge_score
        + MAX_TILE_WEIGHT * max_tile_log
        + (CORNER_BONUS if max_tile_in_corner else 0)
        + MONOTONICITY_WEIGHT * monotonicity_score
        - SMOOTHNESS_WEIGHT * smoothness_score
    )


def max_value(board: list[list[int | None]], depth: int) -> float:
    """Value of a max node: the player picks the move with the best expected score."""
    if has_won(board):
        return WIN_REWARD
    if not has_available_moves(board):
        return LOSS_PENALTY
    if depth <= 0:
        return heuristic_score(board)
    best_score = float('-inf')
    for move in _MOVES.values():
        new_board, score_gained = move(board)
        if new_board == board:  # illegal move, skip it
            continue
        # A move starts the game's "turn", so the spawn happens one level deeper.
        score = score_gained + chance_value(new_board, depth - 1)
        best_score = max(best_score, score)
    return best_score


def chance_value(board: list[list[int | None]], depth: int) -> float:
    """Value of a chance node: the probability-weighted average over every tile spawn."""
    empty_cells = get_empty_cells(board)
    if not empty_cells:  # nothing can spawn; just evaluate the board
        return heuristic_score(board)
    # Each empty cell is equally likely to receive the new tile.
    cell_probability = 1 / len(empty_cells)
    expected_score = 0.0
    for row, col in empty_cells:
        for value, spawn_probability in SPAWN_PROBABILITIES.items():
            spawned_board = [r[:] for r in board]  # shallow row copy is enough for ints/None
            spawned_board[row][col] = value
            # Depth is passed through unchanged: it only ticks down when a move is made.
            expected_score += cell_probability * spawn_probability * max_value(spawned_board, depth)
    return expected_score


def _move_scores(board: list[list[int | None]], depth: int) -> dict[str, float]:
    """Return the expectimax value of every legal move, keyed by direction."""
    scores: dict[str, float] = {}
    for direction, move in _MOVES.items():
        new_board, score_gained = move(board)
        if new_board == board:  # illegal move, skip it
            continue
        scores[direction] = score_gained + chance_value(new_board, depth - 1)
    return scores


def suggest_move(board: list[list[int | None]], depth: int = DEPTH_LIMIT) -> str:
    """Return the best move ('left'/'right'/'up'/'down') via depth-limited expectimax."""
    scores = _move_scores(board, depth)
    if not scores:  # no legal move: the game is over
        return ''
    return max(scores, key=scores.__getitem__)


def move_probabilities(
    board: list[list[int | None]],
    depth: int = DEPTH_LIMIT,
    temperature: float = TEMPERATURE,
) -> dict[str, float]:
    """Return a softmax confidence distribution over the legal moves.

    The expectimax scores are utilities on an arbitrary scale, so they are first
    shifted by their maximum (which keeps ``exp`` numerically stable and leaves
    the distribution unchanged) before the softmax is applied. The returned
    probabilities are non-negative and sum to 1; an empty mapping means the game
    is over (no legal move).
    """
    scores = _move_scores(board, depth)
    if not scores:
        return {}
    highest = max(scores.values())
    exponentials = {
        direction: math.exp((score - highest) / temperature) for direction, score in scores.items()
    }
    total = sum(exponentials.values())
    return {direction: value / total for direction, value in exponentials.items()}


def suggest_move_with_probability(
    board: list[list[int | None]],
    depth: int = DEPTH_LIMIT,
    temperature: float = TEMPERATURE,
) -> tuple[str, float]:
    """Return the best move and its softmax confidence in ``[0, 1]``.

    Returns ``('', 0.0)`` when the game is over (no legal move).
    """
    probabilities = move_probabilities(board, depth, temperature)
    if not probabilities:
        return '', 0.0
    best_move = max(probabilities, key=probabilities.__getitem__)
    return best_move, probabilities[best_move]


if __name__ == '__main__':

    def pretty_print(board):
        for row in board:
            print('+------+------+------+------+')
            print(
                '|' + '|'.join(f'{cell if cell not in {0, None} else "":^6}' for cell in row) + '|'
            )
        print('+------+------+------+------+')

    board: list[list[int | None]] = [
        [2, 4, 8, 16],
        [None, 4, 8, 32],
        [2, None, 16, 64],
        [4, 8, 32, 128],
    ]
    best_move, probability = suggest_move_with_probability(board, depth=DEPTH_LIMIT)
    print(f'Best move: {best_move.upper()} (confidence: {probability:.1%})')
    new_board_for_best_move, _ = _MOVES[best_move](board)
    pretty_print(new_board_for_best_move)
