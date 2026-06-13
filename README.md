# 2048 Home Exercise

A small, from-scratch implementation of the [2048](https://play2048.co) game.

```
home-exercise-2048/
├── backend/
│   ├── src/game2048/
│   │   ├── config.py     # global, tunable game parameters
│   │   ├── engine.py     # pure domain logic (Game class + move functions)
│   │   ├── ai.py         # AI move suggestion (placeholder)
│   │   ├── api.py        # HTTP layer (placeholder)
│   │   └── main.py       # app entrypoint (placeholder)
│   ├── tests/
│   └── pyproject.toml
├── frontend/             # web UI (not started yet)
└── README.md
```

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
cd backend
uv sync          # create .venv and install game2048 (editable) + dev tools
```

## Running the tests

```bash
uv run pytest            # all tests
uv run pytest -v         # verbose
uv run pytest -k move    # filter by name
```

## Linting / formatting

```bash
uv run ruff check .      # lint
uv run ruff format .     # format
```

## Configuration

Game parameters (board size, initial tile count, odds of spawning a `4`, and the
winning value) live in [backend/src/game2048/config.py](backend/src/game2048/config.py).

## Assumptions

- The board is 4x4.
- Empty cells are represented as `None` in Python and `null` in JSON.
- A move is valid only if it changes the board.
- A new tile (`2` or `4`) is added only after a valid move.
- The game is won when any tile reaches `2048`.
- The game is lost when there are no empty cells and no valid moves.
- The AI suggestion (planned) will run offline via a heuristic evaluator; no
  external credentials or remote model are required.
