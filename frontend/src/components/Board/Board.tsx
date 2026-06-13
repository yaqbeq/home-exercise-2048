import type { Board as BoardType } from '../../api'
import { Tile } from '../Tile/Tile'
import './Board.css'

interface BoardProps {
  board: BoardType
}

/** Renders the grid of tiles. Layout is handled by CSS Grid in Board.css. */
export const Board = ({ board }: BoardProps) => {
  return (
    <div className="board">
      {/* Flatten the 2D board into a list of <Tile> elements. */}
      {board.map((row, rowIndex) =>
        row.map((cell, colIndex) => (
          // `key` must be unique/stable so React can track each cell efficiently.
          <Tile key={`${rowIndex}-${colIndex}`} value={cell} />
        )),
      )}
    </div>
  )
}
