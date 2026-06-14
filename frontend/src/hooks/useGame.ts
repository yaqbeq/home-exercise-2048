import { useCallback, useEffect, useState } from 'react'
import { type Board, type Direction, move, newGame } from '../api'

/** High-level game status used to drive the UI. */
export type GameStatus = 'idle' | 'playing' | 'won' | 'lost'

/**
 * A placeholder AI move suggestion. `score` is a 0–1 probability/quality that
 * the (not-yet-implemented) AI assigns to the suggested direction.
 */
export interface Suggestion {
  direction: Direction
  score: number
}

/** Directions the placeholder AI can pick from. */
const DIRECTIONS: Direction[] = ['left', 'right', 'up', 'down']

/** Maps keyboard arrow keys (and WASD) to move directions. */
const KEY_TO_DIRECTION: Record<string, Direction> = {
  ArrowLeft: 'left',
  ArrowRight: 'right',
  ArrowUp: 'up',
  ArrowDown: 'down',
  a: 'left',
  d: 'right',
  w: 'up',
  s: 'down',
}

export interface UseGame {
  board: Board
  score: number
  status: GameStatus
  /** The current AI suggestion, or `null` when none is shown. */
  suggestion: Suggestion | null
  /** Starts (or restarts) a game with a fresh board. */
  start: () => void
  /** Applies a move in the given direction. */
  doMove: (direction: Direction) => void
  /** Requests an AI move suggestion (placeholder — no real AI yet). */
  askAI: () => void
  /** Dismisses the current AI suggestion. */
  dismissSuggestion: () => void
}

/**
 * Owns all client-side game state for the stateless backend: the current
 * board, the accumulated score, and the game status. Moves are sent to the
 * API, which returns the next board; the score is accumulated on the client.
 * Arrow keys (and WASD) are bound while a game is in progress.
 */
export const useGame = (): UseGame => {
  // useState returns [currentValue, setter]; calling the setter re-renders the UI.
  const [board, setBoard] = useState<Board>([])
  const [score, setScore] = useState(0)
  const [status, setStatus] = useState<GameStatus>('idle')
  const [suggestion, setSuggestion] = useState<Suggestion | null>(null)

  // useCallback memoizes the function so it keeps a stable identity across renders.
  const start = useCallback(() => {
    newGame()
      .then((fresh) => {
        setBoard(fresh)
        setScore(0)
        setStatus('playing')
        setSuggestion(null)
      })
      .catch(() => setStatus('idle'))
  }, [])

  const doMove = useCallback(
    (direction: Direction) => {
      if (status !== 'playing') {
        return
      }
      setSuggestion(null)
      move(board, direction)
        .then((result) => {
          if (!result.changed) {
            return // illegal move: nothing changes, no tile spawns
          }
          setBoard(result.board)
          setScore((current) => current + result.score_gained)
          if (result.win) {
            setStatus('won')
          } else if (result.game_over) {
            setStatus('lost')
          }
        })
        .catch(() => {
          /* keep current state on transient errors */
        })
    },
    [board, status],
  )

  // Placeholder AI: picks a random direction and a random confidence score.
  // Real evaluation (offline expectimax) is not implemented yet.
  const askAI = useCallback(() => {
    if (status !== 'playing') {
      return
    }
    const direction = DIRECTIONS[Math.floor(Math.random() * DIRECTIONS.length)]
    setSuggestion({ direction, score: Math.random() })
  }, [status])

  const dismissSuggestion = useCallback(() => setSuggestion(null), [])

  // useEffect runs side effects after render; the cleanup it returns runs before
  // the next effect / on unmount. Re-runs whenever a value in [deps] changes.
  // Bind keyboard controls only while a game is in progress.
  useEffect(() => {
    if (status !== 'playing') {
      return
    }
    const onKeyDown = (event: KeyboardEvent) => {
      const direction = KEY_TO_DIRECTION[event.key]
      if (direction) {
        event.preventDefault()
        doMove(direction)
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [status, doMove])

  return {
    board,
    score,
    status,
    suggestion,
    start,
    doMove,
    askAI,
    dismissSuggestion,
  }
}
