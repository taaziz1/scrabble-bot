from scrabble_game.board import Board
from scrabble_game.models import Position, Square, Tile
from scrabble_game.rack import Rack
from scrabble_game.results import MoveResult, ValidationResult
from scrabble_game.state import GameState, PlayerState


def test_player_state():
    player = PlayerState(name="Alice", rack=Rack([Tile("A", 1)]), score=5)
    assert player.name == "Alice"
    assert len(player.rack) == 1
    assert player.score == 5


def test_game_state_fields(sample_bag):
    board = Board(size=15, premium_squares={})
    players = [PlayerState("Alice", Rack([])), PlayerState("Bob", Rack([]))]
    state = GameState(board=board, players=players, current_player_index=0, bag=sample_bag)

    assert state.current_player_index == 0
    assert state.is_finished is False
    assert state.winner_index is None


def test_validation_result_defaults():
    result = ValidationResult(valid=True)
    assert result.valid is True
    assert result.errors == []
    assert result.words_formed == []
    assert result.word_cells == []
    assert result.newly_placed_positions == set()


def test_move_result_fields(game_state):
    result = MoveResult(
        state=game_state,
        words_formed=["CAT"],
        score_delta=10,
        game_over=False,
    )
    assert result.words_formed == ["CAT"]
    assert result.score_delta == 10
    assert result.game_over is False
    assert result.errors == []