import { useCallback, useEffect, useState, useRef } from 'react'
import {
  type Board,
  type Direction,
  type SuggestionResult,
  move,
  newGame,
  suggest,
  suggestLlm,
} from '../api'

/** High-level game status used to drive the UI. */
export type GameStatus = 'idle' | 'playing' | 'won' | 'lost'

/** Which engine produced a suggestion: the offline expectimax AI or the LLM. */
export type SuggestionSource = 'ai' | 'llm'

/** An active move suggestion shown to the player, tagged with its source. */
export interface Suggestion {
  direction: Direction
  source: SuggestionSource
}

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
  /** The current suggestion (from either engine), or `null` when none is shown. */
  suggestion: Suggestion | null
  /** Which engine is currently computing a suggestion, or `null` when idle. */
  thinking: SuggestionSource | null
  /** Starts (or restarts) a game with a fresh board. */
  start: () => void
  /** Applies a move in the given direction. */
  doMove: (direction: Direction) => void
  /** Requests a suggestion from the offline expectimax AI. */
  askAI: () => void
  /** Requests a suggestion from the remote LLM. */
  askLLM: () => void
  /** Dismisses the current suggestion, whichever engine produced it. */
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
  const [thinking, setThinking] = useState<SuggestionSource | null>(null)

  // Each engine caches its own answers, keyed on the serialized board, so
  // repeat asks are instant and the two engines never share results.
  const aiCache = useRef(new Map<string, Direction>())
  const llmCache = useRef(new Map<string, Direction>())

  // useCallback memoizes the function so it keeps a stable identity across renders.
  const start = useCallback(() => {
    newGame()
      .then((newBoard) => {
        setBoard(newBoard)
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

  // Shared request flow for both engines: serve from the engine's own cache
  // when possible, otherwise show a "thinking" state while the call is in
  // flight and tag the result with its source.
  const requestSuggestion = useCallback(
    (
      source: SuggestionSource,
      fetcher: (board: Board) => Promise<SuggestionResult>,
      cache: Map<string, Direction>,
    ) => {
      if (status !== 'playing') {
        return
      }
      const key = JSON.stringify(board)
      const cached = cache.get(key)
      if (cached) {
        setSuggestion({ direction: cached, source })
        return
      }
      setSuggestion(null)
      setThinking(source)
      fetcher(board)
        .then((result) => {
          cache.set(key, result.direction)
          setSuggestion({ direction: result.direction, source })
        })
        .catch(() => {
          /* keep current state */
        })
        .finally(() => {
          setThinking(null)
        })
    },
    [board, status],
  )

  // AI: offline expectimax via /api/ai.
  const askAI = useCallback(
    () => requestSuggestion('ai', suggest, aiCache.current),
    [requestSuggestion],
  )

  // LLM: remote model via /api/llm.
  const askLLM = useCallback(
    () => requestSuggestion('llm', suggestLlm, llmCache.current),
    [requestSuggestion],
  )

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
    thinking,
    start,
    doMove,
    askAI,
    askLLM,
    dismissSuggestion,
  }
}
