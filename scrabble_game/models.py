from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Tile:
    letter: str
    points: int
    is_blank: bool = False


@dataclass
class Square:
    letter_multiplier: int = 1
    word_multiplier: int = 1
    tile: Optional[Tile] = None


@dataclass(frozen=True)
class Position:
    row: int
    col: int