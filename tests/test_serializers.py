from scrabble_game.models import Tile
from scrabble_game.rack import Rack
from scrabble_game.serializers import (
    bag_from_dict,
    bag_to_dict,
    board_from_dict,
    board_to_dict,
    game_state_from_dict,
    game_state_to_dict,
    rack_from_dict,
    rack_to_dict,
    tile_from_dict,
    tile_to_dict,
)


def test_tile_round_trip():
    tile = Tile("C", 3)
    data = tile_to_dict(tile)
    restored = tile_from_dict(data)

    assert restored == tile


def test_rack_round_trip():
    rack = Rack([Tile("C", 3), Tile("A", 1), Tile("_", 0, is_blank=True)])
    data = rack_to_dict(rack)
    restored = rack_from_dict(data)

    assert [t.letter for t in restored.tiles] == ["C", "A", "_"]
    assert restored.tiles[2].is_blank is True


def test_board_round_trip(empty_board):
    empty_board.place_tile(7, 7, Tile("C", 3))
    data = board_to_dict(empty_board)
    restored = board_from_dict(data)

    assert restored.size == empty_board.size
    assert restored.get_tile(7, 7).letter == "C"
    assert restored.get_square(7, 8).letter_multiplier == empty_board.get_square(7, 8).letter_multiplier


def test_bag_round_trip(sample_bag):
    data = bag_to_dict(sample_bag)
    restored = bag_from_dict(data)

    assert restored.remaining() == sample_bag.remaining()


def test_game_state_round_trip(game_state):
    game_state.board.place_tile(7, 7, Tile("C", 3))
    game_state.players[0].score = 12

    data = game_state_to_dict(game_state)
    restored = game_state_from_dict(data)

    assert restored.current_player_index == game_state.current_player_index
    assert restored.players[0].name == "Alice"
    assert restored.players[0].score == 12
    assert restored.board.get_tile(7, 7).letter == "C"