# 2048 Home Exercise

## Assumptions

- The board is 4x4.
- Empty cells are represented as `None` in Python and `null` in JSON.
- A move is valid only if it changes the board.
- A new tile (`2` or `4`) is added only after a valid move.
- The game is won if any tile reaches `2048`.
- The game is lost if there are no empty cells and no valid moves.
- The AI suggestion is implemented offline using a heuristic move evaluator; no external credentials or remote AI model are required.
