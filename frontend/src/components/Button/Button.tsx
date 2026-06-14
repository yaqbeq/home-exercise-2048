import './Button.css'

/** Visual style of the button. */
type ButtonVariant = 'primary' | 'secondary'

interface ButtonProps {
  label: string
  onClick: () => void
  variant?: ButtonVariant
  disabled?: boolean
}

/**
 * Generic presentational button. It knows nothing about game state: the parent
 * passes the label and the click handler. Used for start/reset, "Ask AI", and
 * the end-game "Play again" action.
 */
export const Button = ({
  label,
  onClick,
  variant = 'primary',
  disabled = false,
}: ButtonProps) => (
  <button
    type="button"
    className={`control-button control-button--${variant}`}
    onClick={onClick}
    disabled={disabled}
  >
    {label}
  </button>
)
