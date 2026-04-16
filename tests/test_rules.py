from scrabble_game.models import Tile
from scrabble_game.move import ExchangeMove, PassMove, Placement, PlayMove
from scrabble_game.rack import Rack
from scrabble_game.rules import validate_move
from scrabble_game.state import GameState, PlayerState


def test_validate_first_move_must_cover_center(config, empty_board, sample_bag, small_dictionary):
    state = GameState(
        board=empty_board,
        players=[
            PlayerState("Alice", Rack([Tile("C", 3), Tile("A", 1), Tile("T", 1)])),
            PlayerState("Bob", Rack([Tile("B", 3), Tile("A", 1), Tile("D", 2)])),
        ],
        current_player_index=0,
        bag=sample_bag,
    )

    move = PlayMove(placements=(
        Placement(row=7, col=8, tile_index_in_rack=0),
        Placement(row=7, col=9, tile_index_in_rack=1),
        Placement(row=7, col=10, tile_index_in_rack=2),
    ))

    result = validate_move(state, move, config, small_dictionary)
    assert result.valid is False
    assert any("center" in error.lower() for error in result.errors)


def test_validate_first_move_center_cat(game_state, config, small_dictionary):
    move = PlayMove(placements=(
        Placement(row=7, col=7, tile_index_in_rack=0),
        Placement(row=7, col=8, tile_index_in_rack=1),
        Placement(row=7, col=9, tile_index_in_rack=2),
    ))

    result = validate_move(game_state, move, config, small_dictionary)
    assert result.valid is True
    assert "CAT" in result.words_formed


def test_validate_duplicate_positions(game_state, config, small_dictionary):
    move = PlayMove(placements=(
        Placement(row=7, col=7, tile_index_in_rack=0),
        Placement(row=7, col=7, tile_index_in_rack=1),
    ))

    result = validate_move(game_state, move, config, small_dictionary)
    assert result.valid is False


def test_validate_out_of_bounds(game_state, config, small_dictionary):
    move = PlayMove(placements=(
        Placement(row=99, col=99, tile_index_in_rack=0),
    ))

    result = validate_move(game_state, move, config, small_dictionary)
    assert result.valid is False


def test_validate_occupied_square(game_state, config, small_dictionary):
    game_state.board.place_tile(7, 7, Tile("B", 3))

    move = PlayMove(placements=(
        Placement(row=7, col=7, tile_index_in_rack=0),
    ))

    result = validate_move(game_state, move, config, small_dictionary)
    assert result.valid is False
    assert any("occupied" in error.lower() for error in result.errors)


def test_validate_rack_index_out_of_range(game_state, config, small_dictionary):
    move = PlayMove(placements=(
        Placement(row=7, col=7, tile_index_in_rack=99),
    ))

    result = validate_move(game_state, move, config, small_dictionary)
    assert result.valid is False


def test_validate_same_rack_index_used_twice(game_state, config, small_dictionary):
    move = PlayMove(placements=(
        Placement(row=7, col=7, tile_index_in_rack=0),
        Placement(row=7, col=8, tile_index_in_rack=0),
    ))

    result = validate_move(game_state, move, config, small_dictionary)
    assert result.valid is False


def test_validate_must_be_single_row_or_column(game_state, config, small_dictionary):
    move = PlayMove(placements=(
        Placement(row=7, col=7, tile_index_in_rack=0),
        Placement(row=8, col=8, tile_index_in_rack=1),
    ))

    result = validate_move(game_state, move, config, small_dictionary)
    assert result.valid is False
    assert any("row or one column" in error.lower() for error in result.errors)


def test_validate_no_gaps_without_bridge(game_state, config, small_dictionary):
    move = PlayMove(placements=(
        Placement(row=7, col=7, tile_index_in_rack=0),
        Placement(row=7, col=9, tile_index_in_rack=1),
    ))

    result = validate_move(game_state, move, config, small_dictionary)
    assert result.valid is False


def test_validate_later_move_must_connect(config, empty_board, sample_bag, small_dictionary):
    empty_board.place_tiles([
        (7, 7, Tile("C", 3)),
        (7, 8, Tile("A", 1)),
        (7, 9, Tile("T", 1)),
    ])

    state = GameState(
        board=empty_board,
        players=[
            PlayerState("Alice", Rack([Tile("B", 3), Tile("A", 1), Tile("D", 2)])),
            PlayerState("Bob", Rack([Tile("C", 3), Tile("A", 1), Tile("T", 1)])),
        ],
        current_player_index=0,
        bag=sample_bag,
    )

    move = PlayMove(placements=(
        Placement(row=0, col=0, tile_index_in_rack=0),
        Placement(row=0, col=1, tile_index_in_rack=1),
        Placement(row=0, col=2, tile_index_in_rack=2),
    ))

    result = validate_move(state, move, config, small_dictionary)
    assert result.valid is False
    assert any("connect" in error.lower() for error in result.errors)


def test_validate_invalid_dictionary_word(game_state, config, small_dictionary):
    move = PlayMove(placements=(
        Placement(row=7, col=7, tile_index_in_rack=0),  # C
        Placement(row=7, col=8, tile_index_in_rack=0),  # invalid repeated index but already covered
    ))

    result = validate_move(game_state, move, config, small_dictionary)
    assert result.valid is False


def test_validate_blank_tile_assignment(config, empty_board, sample_bag, small_dictionary):
    state = GameState(
        board=empty_board,
        players=[
            PlayerState("Alice", Rack([Tile("C", 3), Tile("_", 0, is_blank=True), Tile("T", 1)])),
            PlayerState("Bob", Rack([Tile("B", 3)])),
        ],
        current_player_index=0,
        bag=sample_bag,
    )

    move = PlayMove(placements=(
        Placement(row=7, col=7, tile_index_in_rack=0),
        Placement(row=7, col=8, tile_index_in_rack=1, assigned_letter="A"),
        Placement(row=7, col=9, tile_index_in_rack=2),
    ))

    result = validate_move(state, move, config, small_dictionary)
    assert result.valid is True
    assert "CAT" in result.words_formed


def test_validate_exchange_move_valid(game_state, config, small_dictionary):
    move = ExchangeMove(tile_indices=(0, 1))
    result = validate_move(game_state, move, config, small_dictionary)
    assert result.valid is True


def test_validate_exchange_move_duplicate_indices(game_state, config, small_dictionary):
    move = ExchangeMove(tile_indices=(0, 0))
    result = validate_move(game_state, move, config, small_dictionary)
    assert result.valid is False


def test_validate_exchange_move_not_enough_tiles_in_bag(game_state, config, small_dictionary):
    game_state.bag.draw(game_state.bag.remaining())
    move = ExchangeMove(tile_indices=(0,))
    result = validate_move(game_state, move, config, small_dictionary)
    assert result.valid is False


def test_validate_pass_move(game_state, config, small_dictionary):
    move = PassMove()
    result = validate_move(game_state, move, config, small_dictionary)
    assert result.valid is True