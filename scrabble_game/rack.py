# rack.py

from __future__ import annotations

from dataclasses import dataclass, field

from .models import Tile


@dataclass
class Rack:
    tiles: list[Tile] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.tiles)

    def __iter__(self):
        return iter(self.tiles)

    def __getitem__(self, index: int) -> Tile:
        return self.tiles[index]

    def as_list(self) -> list[Tile]:
        return list(self.tiles)

    def add_tile(self, tile: Tile) -> None:
        self.tiles.append(tile)

    def add_tiles(self, tiles: list[Tile]) -> None:
        self.tiles.extend(tiles)

    def remove_tile_at(self, index: int) -> Tile:
        if index < 0 or index >= len(self.tiles):
            raise IndexError(f"Rack index out of range: {index}")
        return self.tiles.pop(index)

    def remove_tiles_at(self, indices: list[int] | tuple[int, ...]) -> list[Tile]:
        if len(set(indices)) != len(indices):
            raise ValueError("Duplicate rack indices are not allowed.")

        for index in indices:
            if index < 0 or index >= len(self.tiles):
                raise IndexError(f"Rack index out of range: {index}")

        removed: list[Tile] = []
        for index in sorted(indices, reverse=True):
            removed.append(self.tiles.pop(index))

        removed.reverse()
        return removed

    def peek_tiles_at(self, indices: list[int] | tuple[int, ...]) -> list[Tile]:
        if len(set(indices)) != len(indices):
            raise ValueError("Duplicate rack indices are not allowed.")

        result: list[Tile] = []
        for index in indices:
            if index < 0 or index >= len(self.tiles):
                raise IndexError(f"Rack index out of range: {index}")
            result.append(self.tiles[index])

        return result

    def swap_tiles(
        self,
        indices: list[int] | tuple[int, ...],
        new_tiles: list[Tile],
    ) -> list[Tile]:
        removed = self.remove_tiles_at(indices)
        self.add_tiles(new_tiles)
        return removed

    def contains_index(self, index: int) -> bool:
        return 0 <= index < len(self.tiles)

    def is_empty(self) -> bool:
        return not self.tiles

    def clear(self) -> list[Tile]:
        removed = list(self.tiles)
        self.tiles.clear()
        return removed

    def __str__(self) -> str:
        return " ".join(tile.letter for tile in self.tiles)