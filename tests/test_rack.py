import pytest

from scrabble_game.models import Tile
from scrabble_game.rack import Rack


def test_rack_len(sample_rack):
    assert len(sample_rack) == 5


def test_rack_getitem(sample_rack):
    assert sample_rack[0].letter == "C"
    assert sample_rack[1].letter == "A"


def test_add_tile(sample_rack):
    sample_rack.add_tile(Tile("B", 3))
    assert len(sample_rack) == 6
    assert sample_rack[-1].letter == "B"


def test_add_tiles(sample_rack):
    sample_rack.add_tiles([Tile("B", 3), Tile("D", 2)])
    assert len(sample_rack) == 7
    assert sample_rack[-2].letter == "B"
    assert sample_rack[-1].letter == "D"


def test_remove_tile_at(sample_rack):
    removed = sample_rack.remove_tile_at(1)
    assert removed.letter == "A"
    assert len(sample_rack) == 4
    assert [t.letter for t in sample_rack.tiles] == ["C", "T", "S", "_"]


def test_remove_tile_at_invalid_index(sample_rack):
    with pytest.raises(IndexError):
        sample_rack.remove_tile_at(999)


def test_remove_tiles_at(sample_rack):
    removed = sample_rack.remove_tiles_at([1, 3])
    assert [t.letter for t in removed] == ["A", "S"]
    assert [t.letter for t in sample_rack.tiles] == ["C", "T", "_"]


def test_remove_tiles_at_duplicate_indices(sample_rack):
    with pytest.raises(ValueError):
        sample_rack.remove_tiles_at([1, 1])


def test_remove_tiles_at_invalid_index(sample_rack):
    with pytest.raises(IndexError):
        sample_rack.remove_tiles_at([0, 10])


def test_peek_tiles_at(sample_rack):
    peeked = sample_rack.peek_tiles_at([0, 2, 4])
    assert [t.letter for t in peeked] == ["C", "T", "_"]
    assert len(sample_rack) == 5


def test_contains_index(sample_rack):
    assert sample_rack.contains_index(0) is True
    assert sample_rack.contains_index(4) is True
    assert sample_rack.contains_index(5) is False


def test_is_empty_false(sample_rack):
    assert sample_rack.is_empty() is False


def test_clear(sample_rack):
    removed = sample_rack.clear()
    assert len(removed) == 5
    assert sample_rack.is_empty() is True