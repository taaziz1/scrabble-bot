from dataclasses import dataclass
from .constants import (
    BINGO_BONUS,
    BOARD_SIZE,
    CENTER,
    PREMIUM_SQUARES,
    RACK_SIZE,
    TILE_DISTRIBUTION,
    TILE_POINTS,
)
@dataclass(frozen=True)
class GameConfig:
    board_size: int
    rack_size: int
    bingo_bonus: int
    center: tuple[int, int]
    tile_points: dict[str, int]
    tile_distribution: dict[str, int]
    premium_squares: dict[tuple[int, int], tuple[int, int]]

DEFAULT_CONFIG = GameConfig(
    board_size=BOARD_SIZE,
    rack_size=RACK_SIZE,
    bingo_bonus=BINGO_BONUS,
    center=CENTER,
    tile_points=TILE_POINTS,
    tile_distribution=TILE_DISTRIBUTION,
    premium_squares=PREMIUM_SQUARES,
)