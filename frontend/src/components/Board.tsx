import type { Board as BoardType } from '../api'
import { Tile } from './Tile'

interface BoardProps {
  board: BoardType
}

/** Renders the grid of tiles. Layout is handled by CSS Grid in App.css. */
export function Board({ board }: BoardProps) {
  return (
    <div className="board">
      {board.map((row, rowIndex) =>
        row.map((cell, colIndex) => (
          <Tile key={`${rowIndex}-${colIndex}`} value={cell} />
        )),
      )}
    </div>
  )
}
