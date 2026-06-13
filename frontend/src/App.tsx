import './App.css'
import { Board } from './components/Board'
import { Controls } from './components/Controls'
import { Scoreboard } from './components/Scoreboard'
import { useGame } from './hooks/useGame'

function App() {
  const { board, score, status, start } = useGame()

  const hasBoard = board.length > 0

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
            <button type="button" className="control-button" onClick={start}>
              Play again
            </button>
          </div>
        )}
      </div>

      <div className="controls">
        <Controls status={status} onStart={start} />
      </div>
    </main>
  )
}

export default App
