from __future__ import annotations

import random

from .bag import Bag
from .board import Board
from .models import Tile
from .rack import Rack
from .state import GameState, PlayerState


def tile_to_dict(tile: Tile) -> dict:
    return {
        "letter": tile.letter,
        "points": tile.points,
        "is_blank": tile.is_blank,
    }


def tile_from_dict(data: dict) -> Tile:
    return Tile(
        letter=data["letter"],
        points=data["points"],
        is_blank=data.get("is_blank", False),
    )


def rack_to_dict(rack: Rack) -> dict:
    return {
        "tiles": [tile_to_dict(tile) for tile in rack.tiles],
    }


def rack_from_dict(data: dict) -> Rack:
    return Rack(
        tiles=[tile_from_dict(tile_data) for tile_data in data["tiles"]],
    )


def board_to_dict(board: Board) -> dict:
    squares: list[list[dict]] = []

    for row in range(board.size):
        row_data: list[dict] = []
        for col in range(board.size):
            square = board.get_square(row, col)
            row_data.append(
                {
                    "letter_multiplier": square.letter_multiplier,
                    "word_multiplier": square.word_multiplier,
                    "tile": tile_to_dict(square.tile) if square.tile is not None else None,
                }
            )
        squares.append(row_data)

    return {
        "size": board.size,
        "grid": squares,
    }


def board_from_dict(data: dict) -> Board:
    size = data["size"]
    grid_data = data["grid"]

    premium_squares: dict[tuple[int, int], tuple[int, int]] = {}

    for row in range(size):
        for col in range(size):
            square_data = grid_data[row][col]
            letter_multiplier = square_data["letter_multiplier"]
            word_multiplier = square_data["word_multiplier"]

            if letter_multiplier != 1 or word_multiplier != 1:
                premium_squares[(row, col)] = (letter_multiplier, word_multiplier)

    board = Board(size=size, premium_squares=premium_squares)

    for row in range(size):
        for col in range(size):
            square_data = grid_data[row][col]
            tile_data = square_data["tile"]
            if tile_data is not None:
                board.place_tile(row, col, tile_from_dict(tile_data))

    return board


def bag_to_dict(bag: Bag) -> dict:
    return {
        "tiles": [tile_to_dict(tile) for tile in bag._tiles],
    }


def bag_from_dict(data: dict) -> Bag:
    return Bag(
        tiles=[tile_from_dict(tile_data) for tile_data in data["tiles"]],
        rng=random.Random(),
    )


def player_state_to_dict(player: PlayerState) -> dict:
    return {
        "name": player.name,
        "score": player.score,
        "rack": rack_to_dict(player.rack),
    }


def player_state_from_dict(data: dict) -> PlayerState:
    return PlayerState(
        name=data["name"],
        score=data.get("score", 0),
        rack=rack_from_dict(data["rack"]),
    )


def game_state_to_dict(state: GameState) -> dict:
    return {
        "board": board_to_dict(state.board),
        "players": [player_state_to_dict(player) for player in state.players],
        "current_player_index": state.current_player_index,
        "bag": bag_to_dict(state.bag),
        "consecutive_scoreless_turns": state.consecutive_scoreless_turns,
        "is_finished": state.is_finished,
        "winner_index": state.winner_index,
    }


def game_state_from_dict(data: dict) -> GameState:
    return GameState(
        board=board_from_dict(data["board"]),
        players=[player_state_from_dict(player_data) for player_data in data["players"]],
        current_player_index=data["current_player_index"],
        bag=bag_from_dict(data["bag"]),
        consecutive_scoreless_turns=data.get("consecutive_scoreless_turns", 0),
        is_finished=data.get("is_finished", False),
        winner_index=data.get("winner_index"),
    )