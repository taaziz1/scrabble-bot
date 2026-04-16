from collections import Counter
from typing import Iterable

from .config import GameConfig
from .move import ExchangeMove, PassMove, PlayMove
from .models import Tile
from .results import ValidationResult
from .state import GameState


def validate_move(state: GameState, move, config: GameConfig, dictionary) -> ValidationResult:
    if isinstance(move, PlayMove):
        return validate_play_move(state, move, config, dictionary)
    if isinstance(move, ExchangeMove):
        return validate_exchange_move(state, move, config)
    if isinstance(move, PassMove):
        return validate_pass_move(state, move)
    return ValidationResult(valid=False, errors=["Unknown move type."])


def validate_play_move(
    state: GameState,
    move: PlayMove,
    config: GameConfig,
    dictionary,
) -> ValidationResult:
    errors: list[str] = []

    if not move.placements:
        return ValidationResult(valid=False, errors=["Play move must include at least one placement."])

    current_player = state.players[state.current_player_index]
    board = state.board
    rack = current_player.rack

    positions = [(p.row, p.col) for p in move.placements]
    if len(set(positions)) != len(positions):
        errors.append("Move contains duplicate board positions.")

    for placement in move.placements:
        if not board.in_bounds(placement.row, placement.col):
            errors.append(f"Placement out of bounds: ({placement.row}, {placement.col}).")
        elif not board.is_empty_at(placement.row, placement.col):
            errors.append(f"Square already occupied: ({placement.row}, {placement.col}).")

    used_indices = [p.tile_index_in_rack for p in move.placements]
    if len(set(used_indices)) != len(used_indices):
        errors.append("A rack tile index was used more than once.")

    for index in used_indices:
        if index < 0 or index >= len(rack):
            errors.append(f"Rack index out of range: {index}.")

    if errors:
        return ValidationResult(valid=False, errors=errors)

    rows = {p.row for p in move.placements}
    cols = {p.col for p in move.placements}

    if len(rows) != 1 and len(cols) != 1:
        return ValidationResult(valid=False, errors=["Tiles must all be placed in one row or one column."])

    horizontal = len(rows) == 1

    if not _is_contiguous_with_existing_tiles(board, move, horizontal):
        return ValidationResult(valid=False, errors=["Tiles must form one contiguous word line."])

    if board.is_board_empty():
        if not any((p.row, p.col) == config.center for p in move.placements):
            return ValidationResult(valid=False, errors=["First move must cover the center square."])
    else:
        if not _move_touches_existing_tile(board, move):
            return ValidationResult(valid=False, errors=["Move must connect to an existing tile."])

    temp_board = board.clone()
    placed_positions: set[tuple[int, int]] = set()

    for placement in move.placements:
        rack_tile = rack[placement.tile_index_in_rack]
        tile = _resolve_tile_for_placement(rack_tile, placement.assigned_letter, config)
        temp_board.place_tile(placement.row, placement.col, tile)
        placed_positions.add((placement.row, placement.col))

    words = _extract_words_formed(temp_board, move, horizontal)
    word_strings = ["".join(tile.letter for _, _, tile in word) for word in words]

    invalid_words = [word for word in word_strings if not dictionary.contains(word)]
    if invalid_words:
        return ValidationResult(
            valid=False,
            errors=[f"Invalid word(s): {', '.join(invalid_words)}."],
            words_formed=word_strings,
        )

    return ValidationResult(
        valid=True,
        errors=[],
        words_formed=word_strings,
        word_cells=words,
        newly_placed_positions=placed_positions,
    )


def validate_exchange_move(
    state: GameState,
    move: ExchangeMove,
    config: GameConfig,
) -> ValidationResult:
    current_player = state.players[state.current_player_index]
    rack = current_player.rack

    if not move.tile_indices:
        return ValidationResult(valid=False, errors=["Exchange move must include at least one tile index."])

    if state.bag.remaining() < len(move.tile_indices):
        return ValidationResult(valid=False, errors=["Not enough tiles in the bag to exchange."])

    if len(set(move.tile_indices)) != len(move.tile_indices):
        return ValidationResult(valid=False, errors=["Exchange move contains duplicate rack indices."])

    for index in move.tile_indices:
        if index < 0 or index >= len(rack):
            return ValidationResult(valid=False, errors=[f"Rack index out of range: {index}."])

    return ValidationResult(valid=True)


def validate_pass_move(
    state: GameState,
    move: PassMove,
) -> ValidationResult:
    return ValidationResult(valid=True) 

def _resolve_tile_for_placement(rack_tile: Tile, assigned_letter: str | None, config: GameConfig) -> Tile:
    if not rack_tile.is_blank:
        return rack_tile

    if not assigned_letter or len(assigned_letter) != 1 or not assigned_letter.isalpha():
        raise ValueError("Blank tiles must have a single assigned letter.")

    return Tile(letter=assigned_letter.upper(), points=0, is_blank=True)

def _is_contiguous_with_existing_tiles(board, move: PlayMove, horizontal: bool) -> bool:
    positions = {(p.row, p.col) for p in move.placements}

    if horizontal:
        row = move.placements[0].row
        min_col = min(p.col for p in move.placements)
        max_col = max(p.col for p in move.placements)

        for col in range(min_col, max_col + 1):
            if (row, col) in positions:
                continue
            if board.get_tile(row, col) is None:
                return False
        return True

    col = move.placements[0].col
    min_row = min(p.row for p in move.placements)
    max_row = max(p.row for p in move.placements)

    for row in range(min_row, max_row + 1):
        if (row, col) in positions:
            continue
        if board.get_tile(row, col) is None:
            return False
    return True

def _move_touches_existing_tile(board, move: PlayMove) -> bool:
    for placement in move.placements:
        row, col = placement.row, placement.col
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if board.in_bounds(nr, nc) and board.get_tile(nr, nc) is not None:
                return True
    return False

def _extract_words_formed(board, move: PlayMove, horizontal: bool):
    words = []

    main_anchor = move.placements[0]
    main_word = board.collect_word(main_anchor.row, main_anchor.col, horizontal)
    if len(main_word) > 1:
        words.append(main_word)

    for placement in move.placements:
        cross_word = board.collect_word(placement.row, placement.col, not horizontal)
        if len(cross_word) > 1:
            words.append(cross_word)

    if not words:
        words.append(main_word)

    return words