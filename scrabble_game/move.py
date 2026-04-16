from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class Placement:
    row: int
    col: int
    tile_index_in_rack: int
    assigned_letter: Optional[str] = None


@dataclass(frozen=True)
class PlayMove:
    placements: Tuple[Placement, ...]


@dataclass(frozen=True)
class ExchangeMove:
    tile_indices: Tuple[int, ...]


@dataclass(frozen=True)
class PassMove:
    pass