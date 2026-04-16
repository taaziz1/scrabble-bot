import random
from typing import List

from .models import Tile


class Bag:
    def __init__(
        self,
        tiles: List[Tile],
        rng: random.Random | None = None,
    ) -> None:
        self._rng = rng or random.Random()
        self._tiles = list(tiles)
        self._rng.shuffle(self._tiles)

    @classmethod
    def from_distribution(
        cls,
        tile_distribution: dict[str, int],
        tile_points: dict[str, int],
        rng: random.Random | None = None,
    ) -> "Bag":
        tiles: list[Tile] = []

        for letter, count in tile_distribution.items():
            for _ in range(count):
                tiles.append(
                    Tile(
                        letter=letter,
                        points=tile_points[letter],
                        is_blank=(letter == "_"),
                    )
                )

        return cls(tiles=tiles, rng=rng)

    def draw(self, count: int) -> list[Tile]:
        if count < 0:
            raise ValueError("count must be non-negative")

        drawn = self._tiles[:count]
        self._tiles = self._tiles[count:]
        return drawn

    def return_tiles(self, tiles: list[Tile]) -> None:
        self._tiles.extend(tiles)
        self._rng.shuffle(self._tiles)

    def remaining(self) -> int:
        return len(self._tiles)

    def is_empty(self) -> bool:
        return not self._tiles