# 2048 Home Exercise

A small, from-scratch implementation of the [2048](https://play2048.co) game.

It has two parts:

- **`backend/`** — a Python game engine, an offline **expectimax AI** move
  adviser, and a **stateless** FastAPI HTTP API.
- **`frontend/`** — a Vite + React + TypeScript single-page app (the UI).

The backend owns the game rules; the frontend keeps the board and score in
client state and calls the API for each move.

## Exercise requirements

These are the original home-exercise requirements the project satisfies. Where
they conflict with the classic 2048 game, **these requirements win**.

1. **Initial board.** Generate a starting board with a *random number* of `2`s
   placed at random cells.
2. **Move Left.** Slide tiles left, merging equal adjacent tiles.
3. **Move Right.** Slide tiles right, merging equal adjacent tiles.
4. **Move Up / Move Down.** Same merge behaviour on columns.
5. **Spawn after a move.** Add a `2` or `4` at a random empty cell **only after
   a valid move that changes the board**.
6. **Endgame.** Detect **Win** (a tile reaches `2048`) and **Lose** (no empty
   cells and no valid moves remain).
7. **AI suggestion.** During play, let the player ask an AI for the best next
   move to avoid game over and maximise the chance of winning. The AI runs
   **offline** (no network, **no credentials**) — implemented as a
   depth-limited expectimax search (see
   [AI move suggestion](#ai-move-suggestion)).

## Project structure

```text
home-exercise-2048/
├── backend/
│   ├── src/game2048/
│   │   ├── config.py     # tunable game + AI parameters
│   │   ├── engine.py     # pure domain logic (move functions + helpers)
│   │   ├── ai.py         # offline expectimax AI move adviser
│   │   ├── utils.py      # shared direction -> move-function mapping
│   │   ├── api.py        # FastAPI router: POST /api/new, POST /api/move
│   │   └── main.py       # FastAPI app: CORS, router wiring, /health
│   ├── tests/            # test_engine.py, test_api.py, test_ai.py
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── api.ts                # typed fetch client for the backend
│   │   ├── hooks/useGame.ts      # game state + keyboard controls
│   │   ├── components/           # Board, Tile, Scoreboard, Button
│   │   └── App.tsx               # composes the UI
│   └── package.json
├── AGENTS.md
└── README.md
```

## Setup

### Backend

Requires [uv](https://docs.astral.sh/uv/) and Python `>=3.13`.

```bash
cd backend
uv sync          # create .venv and install game2048 (editable) + dev tools
```

### Frontend

Requires [Node.js](https://nodejs.org/) (18+).

```bash
cd frontend
npm install
```

## Running the app

Start the backend and the frontend dev server in separate terminals.

```bash
# terminal 1 — backend API at http://localhost:8000
cd backend
uv run uvicorn game2048.main:app --reload
```

```bash
# terminal 2 — frontend at http://localhost:5173
cd frontend
npm run dev
```

Open <http://localhost:5173> and play with the arrow keys (or W A S D). The Vite
dev server proxies `/api/*` to the backend, so no extra configuration is needed.

Interactive API docs are available at <http://localhost:8000/docs>.

You can also try the AI from the command line without starting the server:

```bash
cd backend
uv run python -m game2048.ai   # prints the suggested move + confidence for a sample board
```

## Features

- **4×4 game engine** with left / right / up / down moves and adjacent-tile
  merging, implemented as pure, side-effect-free functions.
- **Random initial board** of `2`s and a `2`/`4` spawn after every
  board-changing move.
- **Win / lose detection** (reach `2048`, or no moves remain).
- **Stateless HTTP API** — the server stores no game state; every request
  carries the full board.
- **React UI** — board rendering, keyboard controls, live score, start/reset,
  and win/lose feedback.
- **Offline AI adviser** — an expectimax search that suggests the best next move
  and reports a confidence for it (details below).

## API

The API is **stateless**: each request carries the full board and the server
keeps no game state between requests.

- `POST /api/new` → `{ "board": Board }`
- `POST /api/move` with
  `{ "board": Board, "direction": "left" | "right" | "up" | "down" }`
  → `{ "board", "score_gained", "changed", "win", "game_over" }`
- `GET /health` → `{ "status": "ok" }`

A `Board` is a 4×4 array of cells, where a cell is an integer tile or `null` for
an empty cell. A new tile spawns only when a move changes the board. An invalid
`direction` is rejected with HTTP **422** (Pydantic validation).

## AI move suggestion

The AI lives in [backend/src/game2048/ai.py](backend/src/game2048/ai.py) and runs
fully **offline** — it only calls the pure engine functions, makes no network
requests, and uses no credentials.

### Why expectimax

2048 is a single-player game **against chance**, not against an adversary: after
each move the game spawns a tile at a *random* empty cell (a `2` with 90%
probability, a `4` with 10%). Minimax would model that spawn as a worst-case
enemy and play far too pessimistically. **Expectimax** instead replaces the
opponent's "min" layer with a **chance** layer that averages over the possible
spawns, weighted by their probability — which matches how the game actually
behaves.

### Why not an LLM (Claude / ChatGPT / other large models)

A general-purpose large language model is the wrong tool for this problem:

- **It does not fit the requirement.** The AI must run **offline with no
  credentials**. Hosted models (Claude, ChatGPT, etc.) need a network call and
  an API key, which the exercise explicitly forbids committing.
- **2048 is exact search, not language.** The game has clear rules, a small
  branching factor, and a well-defined value to optimise. A few-millisecond
  expectimax search plays this near-optimally; an LLM only *approximates*
  reasoning over the board and would still be slower and less reliable.
- **No probabilistic guarantees.** Expectimax provably weighs the random spawns
  by their true probabilities. An LLM has no such guarantee — it can hallucinate
  illegal moves or miss a forced loss.
- **Cost, latency, and determinism.** The local search is free, instant, and
  deterministic (so it is easy to unit-test). A remote model adds latency, cost,
  and non-determinism for no gain on a 4×4 grid.

In short: an LLM shines at open-ended, fuzzy, language-heavy tasks. 2048 is a
small, well-specified search problem, where a classic algorithm is faster,
cheaper, verifiable, and offline by construction.

### Alternative algorithms

Expectimax was chosen as the best fit, but several other approaches could solve
2048. The main trade-offs:

| Approach | Idea | Pros | Cons |
| --- | --- | --- | --- |
| **Expectimax** *(used here)* | Full tree over moves + weighted-average chance nodes | Models the random spawn exactly; strong with a good heuristic; deterministic and testable | Branching explodes as the board empties; depth must stay small |
| **Greedy / 1-ply heuristic** | Pick the move with the best immediate heuristic | Trivial and instant | Short-sighted; walks into avoidable dead ends |
| **Minimax (+ alpha-beta)** | Treat the spawn as an adversary | Alpha-beta pruning is efficient | *Wrong model* — the spawn is random, not hostile, so it plays too defensively |
| **Monte Carlo Tree Search (MCTS)** | Many random playouts, build a search tree from the results | No hand-tuned heuristic needed; scales to deep lookahead; anytime (stop whenever) | Needs many simulations for stable moves; noisier; more code than expectimax |
| **Reinforcement learning (e.g. DQN)** | Train a network to map board → best move | Very strong once trained; fast at inference | Heavy training pipeline; needs data/compute; a black box that is hard to test |

For a 4×4 board with a known spawn distribution, **expectimax hits the sweet
spot**: it exploits the exact probabilities, stays fully offline and
deterministic, and is small enough to read and unit-test. MCTS is the most
natural alternative if the heuristic ever becomes a bottleneck or the board
grows; RL is overkill for the scope of this exercise.

### How it works

The search alternates two kinds of nodes down to a fixed depth:

- **Max nodes** ("the player's turn") try every legal move and keep the best
  resulting value.
- **Chance nodes** ("the game spawns a tile") enumerate every empty cell ×
  {`2`, `4`} outcome and take the probability-weighted average.

Leaves are reached when the depth limit is hit or the board is terminal. A won
board returns a large positive reward and a lost board a large negative penalty,
so the AI strongly steers toward wins and away from losses. Non-terminal leaves
are scored by a heuristic.

### Heuristic

A non-terminal board is scored as a weighted sum of features that keep a
position healthy:

- **Empty cells** — more open space means more flexibility.
- **Potential merges** — adjacent equal tiles that could combine.
- **Max tile** (log-scaled) — progress toward `2048`.
- **Max tile in a corner** — the proven 2048 strategy of pinning the big tile.
- **Monotonicity** — rows/columns that increase or decrease consistently.
- **Smoothness** — small differences between neighbours, so tiles can merge.

All weights are tunable in
[config.py](backend/src/game2048/config.py).

### Move confidence

Besides the best move, the AI can report a **confidence** for it. The per-move
expectimax scores are turned into a probability distribution with a softmax. The
scores are on an arbitrary, board-size-dependent scale, so a fixed temperature
would be meaningless; instead the temperature is derived from the *spread* of
this turn's scores:

```text
temperature = (best_score - worst_score) / CONFIDENCE_SHARPNESS
```

This keeps the confidence stable regardless of the heuristic weights or the
board size. `CONFIDENCE_SHARPNESS` is a small dimensionless knob (around 3–5):
higher values make the AI more confident in the single best move, lower values
flatten the distribution toward an even split.

### Public functions

- `suggest_move(board, depth)` → the best direction (`''` if the game is over).
- `move_probabilities(board, depth, sharpness)` → a confidence distribution over
  the legal moves (sums to 1; `{}` if the game is over).
- `suggest_move_with_probability(board, depth, sharpness)` →
  `(best_move, confidence)`.

> **Note.** The AI module and its tests are complete, but it is **not yet wired
> into the HTTP API or the UI** — there is no `/api/suggestion` endpoint or
> "Hint" button yet. For now it is exercised via its public functions and the
> `python -m game2048.ai` demo.

## Configuration

Game and AI parameters live in
[backend/src/game2048/config.py](backend/src/game2048/config.py):

- **Game:** board size, initial tile count range, odds of spawning a `4`, and
  the winning value.
- **AI:** search depth, win/loss rewards, the heuristic weights, and the
  confidence sharpness.

## Development

### Backend (run from `backend/`)

```bash
uv run pytest            # all tests
uv run pytest -v         # verbose
uv run ruff check .      # lint
uv run ruff format .     # format
```

### Frontend (run from `frontend/`)

```bash
npm run dev           # dev server (proxies /api -> :8000)
npm run build         # type-check (tsc) + production build
npm run lint          # ESLint (code quality)
npm run format        # Prettier — write
npm run format:check  # Prettier — verify only
```

## Assumptions

- The board is 4×4.
- Empty cells are represented as `None` in Python and `null` in JSON.
- A move is valid only if it changes the board.
- A new tile (`2` or `4`) is added only after a valid move.
- The game is won when any tile reaches `2048`.
- The game is lost when there are no empty cells and no valid moves.
- The AI runs offline via a heuristic expectimax evaluator (no remote model).

## Status

- ✅ Engine, stateless API, and React UI (board, keyboard moves, score,
  start/reset, win/lose) are implemented and tested.
- ✅ Offline expectimax AI adviser (`ai.py`) with heuristic evaluation and
  move-confidence is implemented and tested.
- ⬜ Exposing the AI over the API (`/api/suggestion`) and a frontend "Hint"
  button are not implemented yet.
