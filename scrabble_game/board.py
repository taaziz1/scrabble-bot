from __future__ import annotations

from copy import deepcopy

from .models import Position, Square, Tile


class Board:
    def __init__(
        self,
        size: int,
        premium_squares: dict[tuple[int, int], tuple[int, int]] | None = None,
    ) -> None:
        if size <= 0:
            raise ValueError("Board size must be positive.")

        self.size = size
        self._grid: list[list[Square]] = [
            [Square() for _ in range(size)]
            for _ in range(size)
        ]

        if premium_squares:
            for (row, col), (letter_mult, word_mult) in premium_squares.items():
                if not self.in_bounds(row, col):
                    raise ValueError(
                        f"Premium square position out of bounds: ({row}, {col})"
                    )
                if letter_mult <= 0 or word_mult <= 0:
                    raise ValueError(
                        f"Invalid multipliers at ({row}, {col}): "
                        f"letter={letter_mult}, word={word_mult}"
                    )

                self._grid[row][col] = Square(
                    letter_multiplier=letter_mult,
                    word_multiplier=word_mult,
                    tile=None,
                )

    def clone(self) -> "Board":
        cloned = Board(self.size)
        cloned._grid = deepcopy(self._grid)
        return cloned

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.size and 0 <= col < self.size

    def get_square(self, row: int, col: int) -> Square:
        if not self.in_bounds(row, col):
            raise IndexError(f"Position out of bounds: ({row}, {col})")
        return self._grid[row][col]

    def get_tile(self, row: int, col: int) -> Tile | None:
        return self.get_square(row, col).tile

    def is_empty_at(self, row: int, col: int) -> bool:
        return self.get_tile(row, col) is None

    def place_tile(self, row: int, col: int, tile: Tile) -> None:
        if not self.in_bounds(row, col):
            raise IndexError(f"Position out of bounds: ({row}, {col})")

        square = self._grid[row][col]
        if square.tile is not None:
            raise ValueError(f"Square already occupied at ({row}, {col})")

        square.tile = tile

    def place_tiles(self, placements: list[tuple[int, int, Tile]]) -> None:
        seen_positions: set[tuple[int, int]] = set()

        for row, col, _ in placements:
            if (row, col) in seen_positions:
                raise ValueError(f"Duplicate placement position: ({row}, {col})")
            seen_positions.add((row, col))

        for row, col, tile in placements:
            self.place_tile(row, col, tile)

    def remove_tile(self, row: int, col: int) -> Tile:
        square = self.get_square(row, col)
        if square.tile is None:
            raise ValueError(f"No tile to remove at ({row}, {col})")

        removed = square.tile
        square.tile = None
        return removed

    def is_board_empty(self) -> bool:
        for row in self._grid:
            for square in row:
                if square.tile is not None:
                    return False
        return True

    def occupied_positions(self) -> list[Position]:
        positions: list[Position] = []

        for row in range(self.size):
            for col in range(self.size):
                if self._grid[row][col].tile is not None:
                    positions.append(Position(row=row, col=col))

        return positions

    def _scan_start(self, row: int, col: int, horizontal: bool) -> tuple[int, int]:
        if not self.in_bounds(row, col):
            raise IndexError(f"Position out of bounds: ({row}, {col})")

        delta_row, delta_col = (0, -1) if horizontal else (-1, 0)
        current_row, current_col = row, col

        while self.in_bounds(current_row + delta_row, current_col + delta_col):
            next_row = current_row + delta_row
            next_col = current_col + delta_col

            if self.get_tile(next_row, next_col) is None:
                break

            current_row = next_row
            current_col = next_col

        return current_row, current_col

    def collect_word(
        self,
        row: int,
        col: int,
        horizontal: bool,
    ) -> list[tuple[Position, Square, Tile]]:
        if not self.in_bounds(row, col):
            raise IndexError(f"Position out of bounds: ({row}, {col})")

        if self.get_tile(row, col) is None:
            return []

        start_row, start_col = self._scan_start(row, col, horizontal)
        delta_row, delta_col = (0, 1) if horizontal else (1, 0)

        result: list[tuple[Position, Square, Tile]] = []
        current_row, current_col = start_row, start_col

        while self.in_bounds(current_row, current_col):
            square = self.get_square(current_row, current_col)
            if square.tile is None:
                break

            result.append(
                (
                    Position(row=current_row, col=current_col),
                    square,
                    square.tile,
                )
            )

            current_row += delta_row
            current_col += delta_col

        return result

    @staticmethod
    def word_to_string(word_cells: list[tuple[Position, Square, Tile]]) -> str:
        return "".join(tile.letter for _, _, tile in word_cells)

    def has_adjacent_tile(self, row: int, col: int) -> bool:
        if not self.in_bounds(row, col):
            raise IndexError(f"Position out of bounds: ({row}, {col})")

        neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for delta_row, delta_col in neighbors:
            neighbor_row = row + delta_row
            neighbor_col = col + delta_col

            if self.in_bounds(neighbor_row, neighbor_col):
                if self.get_tile(neighbor_row, neighbor_col) is not None:
                    return True

        return False

    def __str__(self) -> str:
        rows: list[str] = []

        for row in self._grid:
            rendered_row: list[str] = []
            for square in row:
                if square.tile is None:
                    rendered_row.append(".")
                else:
                    rendered_row.append(square.tile.letter)
            rows.append(" ".join(rendered_row))

        return "\n".join(rows)