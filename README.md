# 2048 Home Exercise

A small, from-scratch implementation of the [2048](https://play2048.co) game.

It has two parts:

- **`backend/`** — a Python game engine plus a **stateless** FastAPI HTTP API.
- **`frontend/`** — a Vite + React + TypeScript single-page app (the UI).

The backend owns the game rules; the frontend keeps the board and score in
client state and calls the API for each move.

## Project structure

```text
home-exercise-2048/
├── backend/
│   ├── src/game2048/
│   │   ├── config.py     # tunable game parameters
│   │   ├── engine.py     # pure domain logic (move functions + helpers)
│   │   ├── ai.py         # AI move suggestion (placeholder)
│   │   ├── api.py        # FastAPI router: POST /api/new, POST /api/move
│   │   └── main.py       # FastAPI app: CORS, router wiring, /health
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── api.ts                # typed fetch client for the backend
│   │   ├── hooks/useGame.ts      # game state + keyboard controls
│   │   ├── components/           # Board, Tile, Scoreboard, Controls
│   │   └── App.tsx               # composes the UI
│   └── package.json
├── AGENTS.md
└── README.md
```

## Setup

### Backend

Requires [uv](https://docs.astral.sh/uv/).

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

## API

The API is **stateless**: each request carries the full board and the server
keeps no game state between requests.

- `POST /api/new` → `{ "board": Board }`
- `POST /api/move` with
  `{ "board": Board, "direction": "left" | "right" | "up" | "down" }`
  → `{ "board", "score_gained", "changed", "win", "game_over" }`
- `GET /health` → `{ "status": "ok" }`

A `Board` is a 4×4 array of cells, where a cell is an integer tile or `null` for
an empty cell. A new tile spawns only when a move changes the board.

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

## Configuration

Game parameters (board size, initial tile count, odds of spawning a `4`, and the
winning value) live in
[backend/src/game2048/config.py](backend/src/game2048/config.py).

## Assumptions

- The board is 4×4.
- Empty cells are represented as `None` in Python and `null` in JSON.
- A move is valid only if it changes the board.
- A new tile (`2` or `4`) is added only after a valid move.
- The game is won when any tile reaches `2048`.
- The game is lost when there are no empty cells and no valid moves.
- The AI suggestion (planned) will run offline via a heuristic evaluator by default
- Additional offline AI model will be added as optional choice

## Status

- ✅ Engine, stateless API, and React UI (board, keyboard moves, score,
  start/reset, win/lose) are implemented and tested.
- ⬜ AI move suggestion (`ai.py`) is not implemented yet — an offline
  expectimax evaluator is the planned approach.
