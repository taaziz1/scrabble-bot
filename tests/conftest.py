import pickle
import random
from pathlib import Path

import pytest

from scrabble_game.bag import Bag
from scrabble_game.board import Board
from scrabble_game.config import GameConfig
from scrabble_game.dictionary import PickleDictionary
from scrabble_game.models import Tile
from scrabble_game.rack import Rack
from scrabble_game.state import GameState, PlayerState


@pytest.fixture
def small_tile_points():
    return {
        "A": 1,
        "B": 3,
        "C": 3,
        "D": 2,
        "T": 1,
        "E": 1,
        "S": 1,
        "_": 0,
    }


@pytest.fixture
def small_tile_distribution():
    return {
        "A": 4,
        "B": 2,
        "C": 2,
        "D": 2,
        "T": 4,
        "E": 4,
        "S": 4,
        "_": 1,
    }


@pytest.fixture
def small_dictionary_words():
    return {
        "A",
        "AT",
        "ATE",
        "TEA",
        "EAT",
        "CAT",
        "CATS",
        "BAT",
        "TAB",
        "BAD",
        "DAB",
        "ADS",
        "SAT",
        "SCAT",
    }


@pytest.fixture
def small_dictionary(small_dictionary_words):
    return PickleDictionary(small_dictionary_words)


@pytest.fixture
def tmp_dictionary_pickle(tmp_path, small_dictionary_words):
    path = tmp_path / "test_words.pickle"
    with path.open("wb") as f:
        pickle.dump(set(small_dictionary_words), f)
    return path


@pytest.fixture
def config(small_tile_points, small_tile_distribution):
    return GameConfig(
        board_size=15,
        rack_size=7,
        bingo_bonus=50,
        center=(7, 7),
        tile_points=small_tile_points,
        tile_distribution=small_tile_distribution,
        premium_squares={
            (7, 7): (1, 2),   # double word
            (7, 8): (2, 1),   # double letter
            (7, 9): (3, 1),   # triple letter
            (8, 7): (1, 3),   # triple word
        },
    )


@pytest.fixture
def empty_board(config):
    return Board(size=config.board_size, premium_squares=config.premium_squares)


@pytest.fixture
def sample_bag(small_tile_distribution, small_tile_points):
    return Bag.from_distribution(
        tile_distribution=small_tile_distribution,
        tile_points=small_tile_points,
        rng=random.Random(123),
    )


@pytest.fixture
def sample_rack():
    return Rack([
        Tile("C", 3),
        Tile("A", 1),
        Tile("T", 1),
        Tile("S", 1),
        Tile("_", 0, is_blank=True),
    ])


@pytest.fixture
def game_state(config, empty_board, sample_bag):
    players = [
        PlayerState(name="Alice", rack=Rack([Tile("C", 3), Tile("A", 1), Tile("T", 1)]), score=0),
        PlayerState(name="Bob", rack=Rack([Tile("B", 3), Tile("A", 1), Tile("D", 2)]), score=0),
    ]
    return GameState(
        board=empty_board,
        players=players,
        current_player_index=0,
        bag=sample_bag,
        consecutive_scoreless_turns=0,
        is_finished=False,
        winner_index=None,
    )