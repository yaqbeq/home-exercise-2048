import type { Cell } from '../../api'
import './Tile.css'

interface TileProps {
  value: Cell
}

/**
 * A single board cell. Empty cells render an empty styled square; filled
 * cells show their value and a value-specific colour class (`tile-2`,
 * `tile-4`, ...), capped at `tile-super` for very large tiles.
 */
export function Tile({ value }: TileProps) {
  // Pick a CSS class based on the tile value so each value gets its own colour.
  const className =
    value === null
      ? 'tile tile-empty'
      : `tile tile-${value <= 2048 ? value : 'super'}`

  // `value ?? ''` shows the number, or an empty string when the cell is null.
  return <div className={className}>{value ?? ''}</div>
}
