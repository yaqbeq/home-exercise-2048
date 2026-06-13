import type { GameStatus } from '../hooks/useGame'

interface ControlsProps {
  status: GameStatus
  onStart: () => void
}

/**
 * The primary action button. Before a game it reads "Start Game"; once a game
 * has begun (or ended) it reads "Reset" and starts a fresh board.
 */
export function Controls({ status, onStart }: ControlsProps) {
  const label = status === 'idle' ? 'Start Game' : 'Reset'
  return (
    <button type="button" className="control-button" onClick={onStart}>
      {label}
    </button>
  )
}
