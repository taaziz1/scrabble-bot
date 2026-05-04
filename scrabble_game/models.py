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

    def copy(self):
        s = Square()
        s.letter_multiplier = self.letter_multiplier
        s.word_multiplier = self.word_multiplier
        if self.tile:
            s.tile = Tile(self.tile.letter, self.tile.points, self.tile.is_blank)
        else:
            s.tile = None
        return s


@dataclass(frozen=True)
class Position:
    row: int
    col: int