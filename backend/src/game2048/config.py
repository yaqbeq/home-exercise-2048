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
