from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .bag import Bag
from .board import Board
from .rack import Rack


@dataclass
class PlayerState:
    name: str
    rack: Rack
    score: int = 0


@dataclass
class GameState:
    board: Board
    players: list[PlayerState]
    current_player_index: int
    bag: Bag
    consecutive_scoreless_turns: int = 0
    is_finished: bool = False
    winner_index: Optional[int] = None