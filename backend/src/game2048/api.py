"""HTTP API layer for game2048.

A small, *stateless* REST API: the server keeps no game state between
requests. Each request carries the full board, and the API delegates all
logic to :mod:`game2048.engine`. This keeps the backend a pure wrapper around
the engine and lets any number of server instances handle any request.

Endpoints (mounted under ``/api`` by :mod:`game2048.main`):

- ``POST /api/new``  -> a fresh starting board.
- ``POST /api/move`` -> apply a move to a board and report the outcome.
- ``POST /api/ai``   -> the AI's suggested next move for a board.
"""

from typing import Literal, cast

from fastapi import APIRouter
from pydantic import BaseModel, Field

from game2048 import engine
from game2048.ai import suggest_move
from game2048.utils import _MOVES

router = APIRouter(prefix='/api')

# A board cell is an int tile or ``None`` for an empty cell (``null`` in JSON).
Board = list[list[int | None]]

# The four legal move directions, mapped to their engine implementations.
Direction = Literal['left', 'right', 'up', 'down']


class NewGameResponse(BaseModel):
    """The board for a freshly started game."""

    board: Board


class MoveRequest(BaseModel):
    """A move request: the current board and the direction to move."""

    board: Board
    direction: Direction


class MoveResponse(BaseModel):
    """The outcome of applying a move to a board.

    ``changed`` is ``False`` when the move would not alter the board (an
    illegal move); in that case no new tile is spawned and the board is
    returned unchanged.
    """

    board: Board
    score_gained: int = Field(ge=0)
    changed: bool
    win: bool
    game_over: bool


class SuggestionRequest(BaseModel):
    """A request for an AI move suggestion, containing the current board state."""

    board: Board


class SuggestionResponse(BaseModel):
    """The AI's suggested move direction for a given board state."""

    direction: Direction | None


@router.post('/new', response_model=NewGameResponse)
def new_game() -> NewGameResponse:
    """Starts a new game and returns its initial board."""
    return NewGameResponse(board=engine.generate_initial_board())


@router.post('/move', response_model=MoveResponse)
def move(request: MoveRequest) -> MoveResponse:
    """Applies a move to the given board and reports the new state.

    A new tile is spawned only when the move actually changes the board, per
    the game rules. ``win`` and ``game_over`` are evaluated on the resulting
    board so the client can react to end-game conditions.
    """
    new_board, score_gained = _MOVES[request.direction](request.board)
    changed = new_board != request.board
    if changed:
        engine.place_number(new_board)
    return MoveResponse(
        board=new_board,
        score_gained=score_gained,
        changed=changed,
        win=engine.has_won(new_board),
        game_over=not engine.has_available_moves(new_board),
    )


@router.post('/ai', response_model=SuggestionResponse)
def suggest(request: SuggestionRequest) -> SuggestionResponse:
    """Returns the AI's suggested move direction for the given board state."""
    if not engine.has_available_moves(request.board):
        return SuggestionResponse(direction=None)
    suggested_direction = suggest_move(request.board)
    if suggested_direction not in _MOVES:
        # This should never happen, but just in case the AI returns an invalid move.
        return SuggestionResponse(direction=None)
    return SuggestionResponse(direction=cast(Direction, suggested_direction))
