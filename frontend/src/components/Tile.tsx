import type { Cell } from '../api'

interface TileProps {
  value: Cell
}

/**
 * A single board cell. Empty cells render an empty styled square; filled
 * cells show their value and a value-specific colour class (`tile-2`,
 * `tile-4`, ...), capped at `tile-super` for very large tiles.
 */
export function Tile({ value }: TileProps) {
  const className =
    value === null
      ? 'tile tile-empty'
      : `tile tile-${value <= 2048 ? value : 'super'}`

  return <div className={className}>{value ?? ''}</div>
}
