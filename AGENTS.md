# AGENTS.md

Guidance for AI agents and contributors working in this repository.

## Project overview

A small, from-scratch implementation of the [2048](https://play2048.co) game,
built as a home exercise. It has two parts:

- **`backend/`** — a Python game engine plus a **stateless** FastAPI HTTP API.
- **`frontend/`** — a Vite + React + TypeScript single-page app (the UI).

The backend owns the game rules; the frontend holds the board/score in client
state and calls the API for each move.

## Project requirements

These are the original home-exercise requirements the project must satisfy.
Where they conflict with the classic 2048 game, **these requirements win**.

1. **Initial board.** Generate a starting board with a *random number* of `2`s
   placed at random cells (the exercise example uses a checkerboard of `2`s).
2. **Move Left.** Slide tiles left, merging equal adjacent tiles.
3. **Move Right.** Slide tiles right, merging equal adjacent tiles.
4. **Move Up / Move Down.** Same merge behavior on columns.
5. **Spawn after a move.** Add a `2` or `4` at a random empty cell **only after
   a valid move that changes the board**.
6. **Endgame.** Detect **Win** (a tile reaches `2048`) and **Lose** (no empty
   cells and no valid moves remain).
7. **AI suggestion.** During play, let the player ask an AI for the best next
   move to avoid game over and maximize the chance of winning. May be an offline
   model or a remote server — but **never commit credentials**. (Planned: an
   offline heuristic/expectimax evaluator; not yet implemented.)

Stated assumptions (reasonable choices where the spec is silent):

- Board is **4×4**; empty cells are `None` in Python / `null` in JSON.
- A move is valid only if it changes the board.
- Win value is `2048`; a freshly spawned tile is a `2` (90%) or `4` (10%).
- Goal is a well-structured, maintainable codebase — not raw performance.
- A basic UI is sufficient; extra game features are explicitly out of scope.

## Documentation maintenance

Documentation is part of "done" — keep it in sync with the code.

- **`README.md` (repo root)** is the canonical user-facing documentation
  (setup, how to run, configuration, assumptions). Always update it when
  behavior, commands, or structure change.
- **`AGENTS.md` (this file)** must be kept current so it always reflects the
  real state of the project (structure, conventions, decisions, status). Update
  it alongside the changes that affect it.
- Apply judgment: update the docs for **reasonable, meaningful** changes
  (new/removed modules or endpoints, changed conventions, tooling, workflows,
  architecture decisions, or status). Do **not** churn the docs for trivial
  edits (typo fixes, small internal refactors, comment tweaks).
- Prefer editing the existing README/AGENTS files over creating new markdown
  files. Do not add other docs unless explicitly requested.
- **Markdown style:** all `.md` files must adhere to **markdownlint**
  conventions (consistent heading levels, fenced code blocks with a language,
  surrounding blank lines around headings/lists/code, no trailing whitespace,
  single trailing newline). Keep new and edited markdown lint-clean.

## Repository structure

```text
home-exercise-2048/
├── backend/
│   ├── src/game2048/
│   │   ├── config.py     # tunable game parameters (board size, win value, odds)
│   │   ├── engine.py     # pure domain logic: move functions + helpers
│   │   ├── ai.py         # AI move suggestion (PLACEHOLDER — not implemented yet)
│   │   ├── api.py        # FastAPI router: POST /api/new, POST /api/move
│   │   └── main.py       # FastAPI app: CORS, router wiring, /health
│   ├── tests/
│   │   ├── test_engine.py
│   │   ├── test_api.py
│   │   └── test_ai.py    # placeholder
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── api.ts                # typed fetch client for the backend
│   │   ├── hooks/useGame.ts      # game state + keyboard controls
│   │   ├── components/
│   │   │   ├── Board.tsx
│   │   │   ├── Tile.tsx
│   │   │   ├── Scoreboard.tsx
│   │   │   └── Controls.tsx
│   │   ├── App.tsx               # composes the UI
│   │   ├── App.css               # game/board styling
│   │   └── index.css             # base styling + palette
│   ├── vite.config.ts            # React plugin + dev proxy /api -> :8000
│   └── package.json
└── README.md
```

## Architecture & key decisions

- **Stateless API.** The server keeps **no** game state between requests. Each
  request carries the full board; the API is a thin wrapper around the pure
  engine functions. There is intentionally **no** `Game` class and no
  server-side session store — it was removed in favor of the pure functions as
  the single source of truth.
- **Client owns state.** The board lives in React state (`useGame`); the score
  is accumulated on the client from each move's `score_gained`.
- **Engine is pure.** `engine.py` exposes side-effect-free functions (except
  `place_number`, which uses `random`). Moves return `(new_board, score_gained)`
  and never mutate the input board.
- **AI is offline-only (planned).** `ai.py` is a placeholder. When implemented,
  it must run offline (no network, **no credentials**) — a depth-limited
  expectimax over the engine functions is the intended approach.

## API contract

Routes are mounted under `/api` (see `main.py`).

- `POST /api/new` → `{ "board": Board }`
- `POST /api/move` with `{ "board": Board, "direction": "left"|"right"|"up"|"down" }`
  → `{ "board", "score_gained", "changed", "win", "game_over" }`
- `GET /health` → `{ "status": "ok" }`

Notes:

- `Board` is a 4×4 array of cells; a cell is an `int` tile or `null` for empty.
- An **invalid direction** is rejected with HTTP **422** (Pydantic `Literal`
  validation), not 400.
- A new tile spawns **only** when a move changes the board (`changed: true`).

## Game rules (assumptions)

- The board is 4×4.
- Empty cells are `None` in Python, `null` in JSON.
- A move is valid only if it changes the board.
- A new tile (`2` or `4`) is added only after a valid move.
- Win: any tile reaches `2048`. Lose: no empty cells and no valid moves.

Tunables live in `backend/src/game2048/config.py` (board size, initial tile
count range, odds of spawning a `4`, win value).

## Conventions

### Backend (Python)

- **Tooling:** [uv](https://docs.astral.sh/uv/) for env/deps, **ruff** for lint
  and format, **pytest** for tests. Python `>=3.13`.
- **Style:** ruff format with **single quotes**, line length **100**, LF
  endings. Run `ruff format` before committing.
- **Imports:** sorted by ruff (isort rules). Import engine functions from
  `game2048.engine`.
- **Types:** annotate function signatures; boards are `list[list[int | None]]`.
- **Docstrings:** short, present-tense summaries (see existing modules).
- **Tests:** mirror module names (`test_engine.py`, `test_api.py`). Use
  `TestClient` for API tests; use `monkeypatch` to make `random` deterministic.

### Frontend (TypeScript/React)

- **Tooling:** Vite, ESLint (flat config) for code quality, **Prettier** for
  formatting. `eslint-config-prettier` disables ESLint rules that conflict with
  Prettier, so the two never fight. TypeScript throughout.
- **Style (Prettier — see `frontend/.prettierrc.json`):** single quotes, **no
  semicolons**, trailing commas, 2-space indent, 80-col print width, LF endings.
  Run `npm run format` before committing.
- **Components:** function components, one per file, named exports.
- **Data flow:** keep game state in `useGame`; components stay presentational.
- **API calls:** go through `src/api.ts`; use the native `fetch` (no axios).
- **No new dependencies** unless necessary — prefer plain CSS / built-ins.

## Common commands

Backend (run from `backend/`):

```bash
uv sync                                   # install deps into .venv
uv run pytest                             # run all tests
uv run pytest tests/test_api.py -v        # one file, verbose
uv run ruff check .                       # lint
uv run ruff format .                      # format
uv run uvicorn game2048.main:app --reload # run API at http://localhost:8000
```

Frontend (run from `frontend/`):

```bash
npm install        # install deps
npm run dev        # dev server at http://localhost:5173 (proxies /api -> :8000)
npm run build      # type-check (tsc) + production build
npm run lint       # ESLint (code quality)
npm run format     # Prettier — write
npm run format:check  # Prettier — verify only
```

To run the full app, start the backend and the frontend dev server in separate
terminals; the Vite proxy forwards `/api/*` to the backend.

## Validation before finishing a change

- Backend: `uv run pytest` is green **and** `uv run ruff check .` /
  `uv run ruff format --check .` are clean.
- Frontend: `npm run build` (tsc passes) **and** `npm run lint` and
  `npm run format:check` are clean.

## Current status / next steps

- ✅ Engine, stateless API (`/api/new`, `/api/move`), and React UI (board,
  keyboard moves, score, start/reset, win/lose) are implemented and tested.
- ⬜ **AI move suggestion** (`ai.py`) is not implemented — offline expectimax is
  the planned approach, plus a UI "Hint" button and a backend `/api/suggestion`
  endpoint.

## Guardrails

- Do **not** add credentials, API keys, or remote AI calls. The AI must be
  offline.
- Do **not** reintroduce server-side game state; keep the API stateless.
- Do **not** add dependencies without a clear need.
- Keep **`README.md`** and **`AGENTS.md`** up to date for meaningful changes
  (see *Documentation maintenance*).
