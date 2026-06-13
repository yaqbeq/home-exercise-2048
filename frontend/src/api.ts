// Typed client for the stateless game2048 backend API.
//
// The server holds no game state: every call sends the full board and gets a
// new board back. See backend/src/game2048/api.py for the matching contract.

/** A single cell: a tile value, or `null` for an empty cell. */
export type Cell = number | null

/** The game board: a square grid of cells (4x4 by default). */
export type Board = Cell[][]

/** The four legal move directions. */
export type Direction = 'left' | 'right' | 'up' | 'down'

/** Response from `POST /api/new`. */
interface NewGameResponse {
  board: Board
}

/** Response from `POST /api/move`. */
export interface MoveResult {
  board: Board
  /** Points gained from merges in this move. */
  score_gained: number
  /** Whether the move actually changed the board (illegal moves do not). */
  changed: boolean
  /** Whether a tile reached the winning value. */
  win: boolean
  /** Whether no further moves are possible. */
  game_over: boolean
}

// Generic POST helper: serializes the body to JSON and parses the JSON reply.
// `async` functions return a Promise (JS's await/async, like Python coroutines).
const postJson = async <T>(url: string, body?: unknown): Promise<T> => {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  if (!response.ok) {
    throw new Error(`Request to ${url} failed: ${response.status}`)
  }
  return response.json() as Promise<T>
}

/** Starts a new game and returns its initial board. */
export const newGame = async (): Promise<Board> => {
  const data = await postJson<NewGameResponse>('/api/new')
  return data.board
}

/** Applies a move to the given board and returns the outcome. */
export const move = (board: Board, direction: Direction): Promise<MoveResult> =>
  postJson<MoveResult>('/api/move', { board, direction })
