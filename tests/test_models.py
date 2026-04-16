from scrabble_game.models import Position, Square, Tile


def test_tile_fields():
    tile = Tile(letter="A", points=1)
    assert tile.letter == "A"
    assert tile.points == 1
    assert tile.is_blank is False


def test_blank_tile_fields():
    tile = Tile(letter="_", points=0, is_blank=True)
    assert tile.letter == "_"
    assert tile.points == 0
    assert tile.is_blank is True


def test_square_defaults():
    square = Square()
    assert square.letter_multiplier == 1
    assert square.word_multiplier == 1
    assert square.tile is None


def test_position_fields():
    pos = Position(row=7, col=8)
    assert pos.row == 7
    assert pos.col == 8