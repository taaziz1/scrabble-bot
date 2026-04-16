from scrabble_game.dictionary import PickleDictionary
from scrabble_game.game import ScrabbleGame
from scrabble_game.models import Tile
from scrabble_game.move import ExchangeMove, PassMove, Placement, PlayMove


def test_new_game_deals_tiles(config, small_dictionary_words):
    game = ScrabbleGame(
        config=config,
        player_names=["Alice", "Bob"],
        dictionary=PickleDictionary(set(small_dictionary_words)),
        rng_seed=1,
    )
    state = game.get_state()

    assert len(state.players) == 2
    assert len(state.players[0].rack) == config.rack_size
    assert len(state.players[1].rack) == config.rack_size
    assert state.current_player_index == 0
    assert state.is_finished is False


def test_validate_move_proxy(config, small_dictionary_words):
    game = ScrabbleGame(
        config=config,
        player_names=["Alice", "Bob"],
        dictionary=PickleDictionary(set(small_dictionary_words)),
        rng_seed=1,
    )
    state = game.get_state()
    state.players[0].rack.tiles = [Tile("C", 3), Tile("A", 1), Tile("T", 1)]

    move = PlayMove(placements=(
        Placement(7, 7, 0),
        Placement(7, 8, 1),
        Placement(7, 9, 2),
    ))

    result = game.validate_move(move)
    assert result.valid is True


def test_apply_invalid_move_does_not_mutate_state(config, small_dictionary_words):
    game = ScrabbleGame(
        config=config,
        player_names=["Alice", "Bob"],
        dictionary=PickleDictionary(set(small_dictionary_words)),
        rng_seed=1,
    )
    state_before = game.get_state()
    state_before.players[0].rack.tiles = [Tile("C", 3), Tile("A", 1), Tile("T", 1)]

    move = PlayMove(placements=(
        Placement(0, 0, 0),
        Placement(0, 1, 1),
        Placement(0, 2, 2),
    ))

    result = game.apply_move(move)
    state_after = game.get_state()

    assert result.errors
    assert state_after.board.get_tile(0, 0) is None
    assert state_after.current_player_index == 0


def test_apply_play_move_updates_board_and_score(config, small_dictionary_words):
    game = ScrabbleGame(
        config=config,
        player_names=["Alice", "Bob"],
        dictionary=PickleDictionary(set(small_dictionary_words)),
        rng_seed=1,
    )
    state = game.get_state()
    state.players[0].rack.tiles = [Tile("C", 3), Tile("A", 1), Tile("T", 1)]

    move = PlayMove(placements=(
        Placement(7, 7, 0),
        Placement(7, 8, 1),
        Placement(7, 9, 2),
    ))

    result = game.apply_move(move)

    assert result.errors == []
    assert result.score_delta > 0
    assert game.get_state().board.get_tile(7, 7).letter == "C"
    assert game.get_state().players[0].score == result.score_delta
    assert game.get_state().current_player_index == 1


def test_apply_pass_move(config, small_dictionary_words):
    game = ScrabbleGame(
        config=config,
        player_names=["Alice", "Bob"],
        dictionary=PickleDictionary(set(small_dictionary_words)),
        rng_seed=1,
    )

    result = game.apply_move(PassMove())
    state = game.get_state()

    assert result.errors == []
    assert result.score_delta == 0
    assert state.current_player_index == 1
    assert state.consecutive_scoreless_turns == 1


def test_apply_exchange_move(config, small_dictionary_words):
    game = ScrabbleGame(
        config=config,
        player_names=["Alice", "Bob"],
        dictionary=PickleDictionary(set(small_dictionary_words)),
        rng_seed=1,
    )
    state = game.get_state()
    original_letters = [tile.letter for tile in state.players[0].rack.tiles]

    result = game.apply_move(ExchangeMove(tile_indices=(0, 1)))
    new_letters = [tile.letter for tile in game.get_state().players[0].rack.tiles]

    assert result.errors == []
    assert len(new_letters) == len(original_letters)
    assert game.get_state().current_player_index == 1
    assert game.get_state().consecutive_scoreless_turns == 1


def test_apply_move_rejects_when_game_finished(config, small_dictionary_words):
    game = ScrabbleGame(
        config=config,
        player_names=["Alice", "Bob"],
        dictionary=PickleDictionary(set(small_dictionary_words)),
        rng_seed=1,
    )
    game.get_state().is_finished = True

    result = game.apply_move(PassMove())
    assert result.game_over is True
    assert result.errors


def test_endgame_when_player_goes_out_and_bag_empty(config, small_dictionary_words):
    game = ScrabbleGame(
        config=config,
        player_names=["Alice", "Bob"],
        dictionary=PickleDictionary(set(small_dictionary_words)),
        rng_seed=1,
    )
    state = game.get_state()

    state.bag.draw(state.bag.remaining())
    state.players[0].rack.tiles = [Tile("A", 1)]
    state.players[1].rack.tiles = [Tile("B", 3)]
    state.players[0].score = 10
    state.players[1].score = 5

    move = PlayMove(placements=(Placement(7, 7, 0),))

    result = game.apply_move(move)
    final_state = game.get_state()

    assert final_state.is_finished is True
    assert result.game_over is True
    assert final_state.winner_index is not None