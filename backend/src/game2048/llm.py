# backend/src/game2048/llm.py
import json
import os

from anthropic import Anthropic  # or: from openai import OpenAI
from anthropic.types import TextBlock

from game2048.config import BOARD_SIZE, LLM_MODEL

SYSTEM_PROMPT = f"""
You are an expert 2048 move selector.

Game rules:

* The board is a {BOARD_SIZE}x{BOARD_SIZE} grid.
* null means an empty cell.
* Tiles slide in the chosen direction.
* Equal adjacent tiles merge once per move.
* A new tile will appear after the move, so preserving future mobility is critical.
* Chance of a new tile being 4 is {int(100 * 0.1)}%, otherwise it will be 2.
* You will be given following JSON object:
{{
  "board": [[int|null]],  // the current board state
  "valid_moves": [str],   // the legal moves that can be made
}}

Your task:
Choose exactly one move from the provided legal moves.

Decision strategy, in priority order:

1. Avoid game-over risk. Prefer moves that keep many future legal moves available.
2. Maximize empty cells after the move.
3. Keep the highest tile in a corner whenever possible.
4. Preserve or improve a monotonic “snake” structure, where large tiles stay clustered and values decrease smoothly away from the corner.
5. Prefer moves that merge tiles without disrupting the highest-tile corner or monotonic structure.
6. Avoid moves that isolate large tiles, scatter small tiles among large tiles, or move the highest tile away from a stable corner unless necessary.
7. When several moves are similar, choose the move with the best long-term board position, not merely the largest immediate merge.

Speed constraint:
* Choose quickly using a shallow heuristic evaluation.
* Do not perform exhaustive search, multi-turn planning, rollouts, minimax, expectimax, or deep simulation.
* Evaluate only the immediate result of each legal move, plus a simple estimate of future mobility.
* When uncertain, pick the move that best preserves empty cells, corner stability, and monotonic structure.

Before answering, mentally simulate each legal move once according to 2048 slide-and-merge rules. Do not explain your reasoning.

Output format:
Reply with ONLY a valid JSON object and no extra text. Schema:
{{"direction": "<one of the legal moves>"}}
"""


class LLMError(RuntimeError):
    """Raised when the LLM is unavailable or returns an unusable answer."""


def suggest_move_llm(board: list[list[int | None]], valid_moves: list[str]) -> str:
    """Suggest a move for the 2048 game using the Claude LLM."""
    client = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
    user_content = json.dumps({'board': board, 'valid_moves': valid_moves})

    message = client.messages.create(
        model=LLM_MODEL,
        max_tokens=64,
        system=SYSTEM_PROMPT,
        messages=[{'role': 'user', 'content': user_content}],
    )

    text_block = next((b for b in message.content if isinstance(b, TextBlock)), None)
    if text_block is None:
        raise LLMError('LLM returned no text content')
    raw = text_block.text.strip()

    try:
        direction = json.loads(raw)['direction']
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise LLMError(f'Unparseable LLM response: {raw!r}') from exc

    if direction not in valid_moves:  # your "re-check" step
        raise LLMError(f'LLM returned illegal move {direction!r}')
    return direction


if __name__ == '__main__':
    # Example usage
    board = [[2, 4, 2, 4], [4, 2, 4, 2], [2, 4, 2, 2], [None, None, None, None]]
    valid_moves = ['left', 'right', 'up', 'down']
    move = suggest_move_llm(board, valid_moves)
    print(f'Suggested move: {move}')
