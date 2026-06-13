import type { GameStatus } from '../../hooks/useGame'
import './Controls.css'

interface ControlsProps {
  status: GameStatus
  onStart: () => void
}

/**
 * The primary action button. Before a game it reads "Start Game"; once a game
 * has begun (or ended) it reads "Reset" and starts a fresh board.
 */
export const Controls = ({ status, onStart }: ControlsProps) => {
  const label = status === 'idle' ? 'Start Game' : 'Reset'
  // `onClick` wires the button to the callback passed in from the parent.
  return (
    <button type="button" className="control-button" onClick={onStart}>
      {label}
    </button>
  )
}
