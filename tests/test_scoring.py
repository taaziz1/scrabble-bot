from scrabble_game.models import Position, Square, Tile
from scrabble_game.scoring import score_play_move, score_word, tile_points_for_scoring


def test_tile_points_for_scoring_regular_tile():
    assert tile_points_for_scoring(Tile("C", 3)) == 3


def test_tile_points_for_scoring_blank_tile():
    assert tile_points_for_scoring(Tile("Z", 0, is_blank=True)) == 0


def test_score_word_simple():
    word_cells = [
        (Position(7, 7), Square(tile=Tile("C", 3)), Tile("C", 3)),
        (Position(7, 8), Square(tile=Tile("A", 1)), Tile("A", 1)),
        (Position(7, 9), Square(tile=Tile("T", 1)), Tile("T", 1)),
    ]
    newly_placed = {(7, 7), (7, 8), (7, 9)}
    assert score_word(word_cells, newly_placed) == 5


def test_score_word_applies_letter_multiplier_only_to_new_tiles():
    word_cells = [
        (Position(7, 7), Square(letter_multiplier=2, tile=Tile("C", 3)), Tile("C", 3)),
        (Position(7, 8), Square(tile=Tile("A", 1)), Tile("A", 1)),
        (Position(7, 9), Square(tile=Tile("T", 1)), Tile("T", 1)),
    ]
    newly_placed = {(7, 7), (7, 8), (7, 9)}
    assert score_word(word_cells, newly_placed) == 8


def test_score_word_applies_word_multiplier():
    word_cells = [
        (Position(7, 7), Square(word_multiplier=2, tile=Tile("C", 3)), Tile("C", 3)),
        (Position(7, 8), Square(tile=Tile("A", 1)), Tile("A", 1)),
        (Position(7, 9), Square(tile=Tile("T", 1)), Tile("T", 1)),
    ]
    newly_placed = {(7, 7), (7, 8), (7, 9)}
    assert score_word(word_cells, newly_placed) == 10


def test_score_word_does_not_reuse_old_premium_square():
    word_cells = [
        (Position(7, 7), Square(letter_multiplier=3, tile=Tile("C", 3)), Tile("C", 3)),
        (Position(7, 8), Square(tile=Tile("A", 1)), Tile("A", 1)),
    ]
    newly_placed = {(7, 8)}
    assert score_word(word_cells, newly_placed) == 4


def test_score_word_blank_tile_scores_zero():
    word_cells = [
        (Position(7, 7), Square(tile=Tile("C", 3)), Tile("C", 3)),
        (Position(7, 8), Square(tile=Tile("A", 0, is_blank=True)), Tile("A", 0, is_blank=True)),
        (Position(7, 9), Square(tile=Tile("T", 1)), Tile("T", 1)),
    ]
    newly_placed = {(7, 7), (7, 8), (7, 9)}
    assert score_word(word_cells, newly_placed) == 4


def test_score_play_move_multiple_words(config):
    word1 = [
        (Position(7, 7), Square(tile=Tile("C", 3)), Tile("C", 3)),
        (Position(7, 8), Square(tile=Tile("A", 1)), Tile("A", 1)),
        (Position(7, 9), Square(tile=Tile("T", 1)), Tile("T", 1)),
    ]
    word2 = [
        (Position(7, 8), Square(tile=Tile("A", 1)), Tile("A", 1)),
        (Position(8, 8), Square(tile=Tile("T", 1)), Tile("T", 1)),
    ]
    newly_placed = {(7, 7), (7, 8), (7, 9), (8, 8)}
    assert score_play_move([word1, word2], newly_placed, config) == 7


def test_score_play_move_bingo_bonus(config):
    word = [
        (Position(7, 7), Square(tile=Tile("A", 1)), Tile("A", 1)),
    ]
    newly_placed = {(0, i) for i in range(config.rack_size)}
    assert score_play_move([word], newly_placed, config) == 1 + config.bingo_bonus