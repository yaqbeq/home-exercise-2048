"""game2048 — a small, framework-free implementation of the 2048 game.

The public surface lives in :mod:`game2048.engine`; tunables live in
:mod:`game2048.config`.
"""

from game2048.engine import Game

__all__ = ['Game']

__version__ = '0.1.0'
