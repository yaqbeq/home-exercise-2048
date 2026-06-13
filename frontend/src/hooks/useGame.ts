import { useCallback, useEffect, useState } from 'react'
import { type Board, type Direction, move, newGame } from '../api'

/** High-level game status used to drive the UI. */
export type GameStatus = 'idle' | 'playing' | 'won' | 'lost'

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
  /** Starts (or restarts) a game with a fresh board. */
  start: () => void
  /** Applies a move in the given direction. */
  doMove: (direction: Direction) => void
}

/**
 * Owns all client-side game state for the stateless backend: the current
 * board, the accumulated score, and the game status. Moves are sent to the
 * API, which returns the next board; the score is accumulated on the client.
 * Arrow keys (and WASD) are bound while a game is in progress.
 */
export function useGame(): UseGame {
  const [board, setBoard] = useState<Board>([])
  const [score, setScore] = useState(0)
  const [status, setStatus] = useState<GameStatus>('idle')

  const start = useCallback(() => {
    newGame()
      .then((fresh) => {
        setBoard(fresh)
        setScore(0)
        setStatus('playing')
      })
      .catch(() => setStatus('idle'))
  }, [])

  const doMove = useCallback(
    (direction: Direction) => {
      if (status !== 'playing') {
        return
      }
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

  return { board, score, status, start, doMove }
}
