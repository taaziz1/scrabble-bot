import pytest

from scrabble_game.models import Tile


def test_board_in_bounds(empty_board):
    assert empty_board.in_bounds(0, 0) is True
    assert empty_board.in_bounds(14, 14) is True
    assert empty_board.in_bounds(-1, 0) is False
    assert empty_board.in_bounds(15, 0) is False


def test_get_square_out_of_bounds(empty_board):
    with pytest.raises(IndexError):
        empty_board.get_square(99, 99)


def test_place_tile_and_get_tile(empty_board):
    tile = Tile("C", 3)
    empty_board.place_tile(7, 7, tile)
    assert empty_board.get_tile(7, 7) == tile
    assert empty_board.is_empty_at(7, 7) is False


def test_place_tile_on_occupied_square(empty_board):
    empty_board.place_tile(7, 7, Tile("C", 3))
    with pytest.raises(ValueError):
        empty_board.place_tile(7, 7, Tile("A", 1))


def test_board_empty_check(empty_board):
    assert empty_board.is_board_empty() is True
    empty_board.place_tile(7, 7, Tile("C", 3))
    assert empty_board.is_board_empty() is False


def test_clone_independent(empty_board):
    empty_board.place_tile(7, 7, Tile("C", 3))
    cloned = empty_board.clone()
    cloned.place_tile(7, 8, Tile("A", 1))

    assert empty_board.get_tile(7, 8) is None
    assert cloned.get_tile(7, 8).letter == "A"


def test_place_tiles(empty_board):
    empty_board.place_tiles([
        (7, 7, Tile("C", 3)),
        (7, 8, Tile("A", 1)),
        (7, 9, Tile("T", 1)),
    ])
    assert empty_board.get_tile(7, 7).letter == "C"
    assert empty_board.get_tile(7, 8).letter == "A"
    assert empty_board.get_tile(7, 9).letter == "T"


def test_place_tiles_duplicate_position(empty_board):
    with pytest.raises(ValueError):
        empty_board.place_tiles([
            (7, 7, Tile("C", 3)),
            (7, 7, Tile("A", 1)),
        ])


def test_remove_tile(empty_board):
    empty_board.place_tile(7, 7, Tile("C", 3))
    removed = empty_board.remove_tile(7, 7)
    assert removed.letter == "C"
    assert empty_board.get_tile(7, 7) is None


def test_remove_tile_missing(empty_board):
    with pytest.raises(ValueError):
        empty_board.remove_tile(7, 7)


def test_collect_word_horizontal(empty_board):
    empty_board.place_tiles([
        (7, 7, Tile("C", 3)),
        (7, 8, Tile("A", 1)),
        (7, 9, Tile("T", 1)),
    ])
    cells = empty_board.collect_word(7, 8, horizontal=True)
    assert empty_board.word_to_string(cells) == "CAT"


def test_collect_word_vertical(empty_board):
    empty_board.place_tiles([
        (7, 7, Tile("C", 3)),
        (8, 7, Tile("A", 1)),
        (9, 7, Tile("T", 1)),
    ])
    cells = empty_board.collect_word(8, 7, horizontal=False)
    assert empty_board.word_to_string(cells) == "CAT"


def test_collect_word_empty_cell_returns_empty(empty_board):
    assert empty_board.collect_word(7, 7, horizontal=True) == []


def test_has_adjacent_tile(empty_board):
    empty_board.place_tile(7, 7, Tile("C", 3))
    assert empty_board.has_adjacent_tile(7, 8) is True
    assert empty_board.has_adjacent_tile(8, 7) is True
    assert empty_board.has_adjacent_tile(0, 0) is False


def test_premium_square_loaded_from_config(empty_board):
    square = empty_board.get_square(7, 8)
    assert square.letter_multiplier == 2
    assert square.word_multiplier == 1