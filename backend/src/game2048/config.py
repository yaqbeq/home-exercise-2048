"""Global configuration for the 2048 game.

Central place for tunable game parameters. Adjust these values to change the
behaviour of the engine (board size, initial tiles, odds of spawning a 4, and
the winning tile value).
"""

# Board geometry
BOARD_SIZE = 4

# How many tiles to place when a new game starts (inclusive range).
MIN_INITIAL_NUMBERS = 2
MAX_INITIAL_NUMBERS = 8

# Probability that a newly spawned tile is a 4 instead of a 2 (0.0 - 1.0).
CHANCE_OF_FOUR = 0.1

# The game is won as soon as any tile reaches this value.
WIN_VALUE = 2048


# --------------------------------------------------------------------------- #
# AI move suggestion (expectimax)
# --------------------------------------------------------------------------- #

# How many plies (a player move plus the tile spawn that follows) the search
# looks ahead. Higher is stronger but exponentially slower.
DEPTH_LIMIT = 3

# Terminal-state values for the search. Large magnitudes so the AI strongly
# prefers winning lines and avoids losing ones, regardless of accumulated score.
WIN_REWARD = 1_000_000.0
LOSS_PENALTY = -1_000_000.0

# Heuristic weights for non-terminal boards. They balance the features that keep
# a position playable: open space, ready merges, a big tile pinned to a corner,
# and tidy (monotonic / smooth) rows and columns.
EMPTY_WEIGHT = 1000  # more empty cells means more flexibility
MERGE_WEIGHT = 500  # potential merges mean more chances to combine tiles
MAX_TILE_WEIGHT = 1000  # a higher max tile is closer to winning
CORNER_BONUS = 2000  # the max tile in a corner is easier to build around
MONOTONICITY_WEIGHT = 100  # monotonic rows/columns are easier to manage
SMOOTHNESS_WEIGHT = 10  # similar neighbours are easier to merge

# --------------------------------------------------------------------------- #
# Claude AI model selection
# --------------------------------------------------------------------------- #
LLM_MODEL = 'claude-sonnet-4-6'
