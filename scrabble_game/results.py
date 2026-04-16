from __future__ import annotations

from dataclasses import dataclass, field

from .models import Position, Square, Tile
from .state import GameState


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    words_formed: list[str] = field(default_factory=list)
    score: int = 0
    word_cells: list[list[tuple[Position, Square, Tile]]] = field(default_factory=list)
    newly_placed_positions: set[tuple[int, int]] = field(default_factory=set)


@dataclass
class MoveResult:
    state: GameState
    words_formed: list[str]
    score_delta: int
    game_over: bool
    errors: list[str] = field(default_factory=list)