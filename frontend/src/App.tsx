import './App.css'
import { Board } from './components/Board/Board'
import { Button } from './components/Button/Button'
import { Scoreboard } from './components/Scoreboard/Scoreboard'
import { useGame, type SuggestionSource } from './hooks/useGame'

/** Human-readable labels for each move direction. */
const DIRECTION_LABEL: Record<string, string> = {
  left: 'Left',
  right: 'Right',
  up: 'Up',
  down: 'Down',
}

/** Human-readable name for each suggestion engine. */
const SOURCE_LABEL: Record<SuggestionSource, string> = {
  ai: 'AI',
  llm: 'Claude',
}

// Top-level component: wires game state to the UI pieces.
const App = () => {
  // Pull live game state + actions from the custom hook (see hooks/useGame.ts).
  const {
    board,
    score,
    status,
    suggestion,
    thinking,
    start,
    askAI,
    askLLM,
    dismissSuggestion,
  } = useGame()

  const hasBoard = board.length > 0
  const isPlaying = status === 'playing'
  const isBusy = thinking !== null
  const startLabel = status === 'idle' ? 'Start Game' : 'Reset'

  // JSX below is the rendered UI; `{...}` embeds JS expressions into the markup.
  return (
    <main className="app">
      <header className="app-header">
        <h1 className="title">2048</h1>
        <Scoreboard score={score} />
      </header>

      <p className="instructions">
        Use the arrow keys (or W A S D) to move the tiles. Merge equal tiles to
        reach <strong>2048</strong>.
      </p>

      <div className="board-area">
        {hasBoard ? (
          <Board board={board} />
        ) : (
          <div className="board board-placeholder">
            <span>Press “Start Game” to play.</span>
          </div>
        )}

        {(status === 'won' || status === 'lost') && (
          <div className={`overlay overlay-${status}`}>
            <p className="overlay-message">
              {status === 'won' ? 'You win! 🎉' : 'Game over'}
            </p>
            <Button label="Play again" onClick={start} />
          </div>
        )}

        {thinking && (
          <div className="overlay overlay-suggestion">
            <p className="overlay-message thinking-dots">
              {`${SOURCE_LABEL[thinking]} is thinking`}
            </p>
          </div>
        )}

        {suggestion && !thinking && (
          <div className="overlay overlay-suggestion">
            <p className="overlay-message">
              {`${SOURCE_LABEL[suggestion.source]} suggests: ${DIRECTION_LABEL[suggestion.direction]}`}
            </p>
            <Button label="Dismiss" onClick={dismissSuggestion} />
          </div>
        )}
      </div>

      <div className="controls">
        <Button label={startLabel} onClick={start} />
        <Button
          label="Ask AI"
          onClick={askAI}
          variant="secondary"
          disabled={!isPlaying || isBusy}
        />
        <Button
          label="Ask Claude"
          onClick={askLLM}
          variant="secondary"
          disabled={!isPlaying || isBusy}
        />
      </div>
    </main>
  )
}

export default App
