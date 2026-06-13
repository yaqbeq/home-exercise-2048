import './Scoreboard.css'

interface ScoreboardProps {
  score: number
}

/** Displays the current score. */
export function Scoreboard({ score }: ScoreboardProps) {
  return (
    <div className="scoreboard">
      <span className="scoreboard-label">Score</span>
      <span className="scoreboard-value">{score}</span>
    </div>
  )
}
