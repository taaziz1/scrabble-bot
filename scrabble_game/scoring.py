from .config import GameConfig
from .models import Position, Square, Tile
from .move import PlayMove
from .state import GameState


def tile_points_for_scoring(tile: Tile) -> int:
    return 0 if tile.is_blank else tile.points


def score_word(
    word_cells: list[tuple[Position, Square, Tile]],
    newly_placed_positions: set[tuple[int, int]],
) -> int:
    word_total = 0
    word_multiplier = 1

    for position, square, tile in word_cells:
        base_points = tile_points_for_scoring(tile)

        if (position.row, position.col) in newly_placed_positions:
            word_total += base_points * square.letter_multiplier
            word_multiplier *= square.word_multiplier
        else:
            word_total += base_points

    return word_total * word_multiplier


def score_play_move(
    word_cells: list[list[tuple[Position, Square, Tile]]],
    newly_placed_positions: set[tuple[int, int]],
    config: GameConfig,
) -> int:
    total_score = 0

    for word in word_cells:
        total_score += score_word(word, newly_placed_positions)

    if len(newly_placed_positions) == config.rack_size:
        total_score += config.bingo_bonus

    return total_score