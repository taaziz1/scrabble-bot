from scrabble_game.config import DEFAULT_CONFIG
from scrabble_game.dictionary import PickleDictionary
from scrabble_game.game import ScrabbleGame
from scrabble_game.models import Tile
from scrabble_game.move import Placement, PlayMove, ExchangeMove, PassMove


def print_board(board) -> None:
    print(board)
    print()


def print_scores(state) -> None:
    for player in state.players:
        rack_letters = [tile.letter for tile in player.rack]
        print(f"{player.name}: score={player.score}, rack={rack_letters}")
    print()


def main() -> None:
    dictionary = PickleDictionary.from_pickle("NWL2023.pickle")

    game = ScrabbleGame(
        config=DEFAULT_CONFIG,
        player_names=["Alice", "Bob"],
        dictionary=dictionary,
        rng_seed=42,
    )

    state = game.get_state()

    # Force a predictable rack for demo purposes
    state.players[0].rack.tiles = [
        Tile("C", 3),
        Tile("A", 1),
        Tile("T", 1),
        Tile("S", 1),
        Tile("E", 1),
        Tile("D", 2),
        Tile("B", 3),
    ]

    print("Initial state")
    print_board(state.board)
    print_scores(state)

    move = PlayMove(placements=(
        Placement(row=7, col=7, tile_index_in_rack=3),
        Placement(row=7, col=8, tile_index_in_rack=2),
        Placement(row=7, col=9, tile_index_in_rack=4),
        Placement(row=7, col=10, tile_index_in_rack=1),
        Placement(row=7, col=11, tile_index_in_rack=5)
    ))

    validation = game.validate_move(move)
    print("Validation result:")
    print(f"valid={validation.valid}")
    print(f"errors={validation.errors}")
    print(f"words_formed={validation.words_formed}")
    print()

    result = game.apply_move(move)
    print("After move:")
    print(f"score_delta={result.score_delta}")
    print(f"words_formed={result.words_formed}")
    print(f"errors={result.errors}")
    print()

    new_state = game.get_state()
    print_board(new_state.board)
    print_scores(new_state)

    move = PlayMove(placements=(
        Placement(row=6, col=9, tile_index_in_rack=4),
        Placement(row=8, col=9, tile_index_in_rack=6),
        Placement(row=9, col=9, tile_index_in_rack=1)
    ))
    validation = game.validate_move(move)
    print("Validation result:")
    print(f"valid={validation.valid}")
    print(f"errors={validation.errors}")
    print(f"words_formed={validation.words_formed}")
    print()

    result = game.apply_move(move)
    print("After move:")
    print(f"score_delta={result.score_delta}")
    print(f"words_formed={result.words_formed}")
    print(f"errors={result.errors}")
    print()

    new_state = game.get_state()
    print_board(new_state.board)
    print_scores(new_state)

    move = ExchangeMove((1,3,4,5));
    validation = game.validate_move(move)
    print("Validation result:")
    print(f"valid={validation.valid}")
    print(f"errors={validation.errors}")
    print(f"words_formed={validation.words_formed}")
    print()

    result = game.apply_move(move)
    print("After move:")
    print(f"score_delta={result.score_delta}")
    print(f"words_formed={result.words_formed}")
    print(f"errors={result.errors}")
    print()

    new_state = game.get_state()
    print_board(new_state.board)
    print_scores(new_state)

    move = PlayMove(placements=(
        Placement(row=5, col=7, tile_index_in_rack=0),
        Placement(row=6, col=7, tile_index_in_rack=4),
        Placement(row=8, col=7, tile_index_in_rack=6),
        Placement(row=9, col=7, tile_index_in_rack=3)
    ))
    validation = game.validate_move(move)
    print("Validation result:")
    print(f"valid={validation.valid}")
    print(f"errors={validation.errors}")
    print(f"words_formed={validation.words_formed}")
    print()

    result = game.apply_move(move)
    print("After move:")
    print(f"score_delta={result.score_delta}")
    print(f"words_formed={result.words_formed}")
    print(f"errors={result.errors}")
    print()

    new_state = game.get_state()
    print_board(new_state.board)
    print_scores(new_state)
    
    move = PlayMove(placements=(
        Placement(row=8, col=3, tile_index_in_rack=2),
        Placement(row=8, col=4, tile_index_in_rack=5),
        Placement(row=8, col=5, tile_index_in_rack=4),
        Placement(row=8, col=6, tile_index_in_rack=6)
    ))
    validation = game.validate_move(move)
    print("Validation result:")
    print(f"valid={validation.valid}")
    print(f"errors={validation.errors}")
    print(f"words_formed={validation.words_formed}")
    print()

    result = game.apply_move(move)
    print("After move:")
    print(f"score_delta={result.score_delta}")
    print(f"words_formed={result.words_formed}")
    print(f"errors={result.errors}")
    print()

    new_state = game.get_state()
    print_board(new_state.board)
    print_scores(new_state)


    move = PlayMove(placements=(
        Placement(row=4, col=4, tile_index_in_rack=2),
        Placement(row=5, col=4, tile_index_in_rack=3),
        Placement(row=6, col=4, tile_index_in_rack=4),
        Placement(row=7, col=4, tile_index_in_rack=0)
    ))
    validation = game.validate_move(move)
    print("Validation result:")
    print(f"valid={validation.valid}")
    print(f"errors={validation.errors}")
    print(f"words_formed={validation.words_formed}")
    print()

    result = game.apply_move(move)
    print("After move:")
    print(f"score_delta={result.score_delta}")
    print(f"words_formed={result.words_formed}")
    print(f"errors={result.errors}")
    print()

    new_state = game.get_state()
    print_board(new_state.board)
    print_scores(new_state)



if __name__ == "__main__":
    main()
from scrabble_game.config import DEFAULT_CONFIG
from scrabble_game.dictionary import PickleDictionary
from scrabble_game.game import ScrabbleGame
from scrabble_game.models import Tile
from scrabble_game.move import Placement, PlayMove


def print_board(board) -> None:
    print(board)
    print()


def print_scores(state) -> None:
    for player in state.players:
        rack_letters = [tile.letter for tile in player.rack]
        print(f"{player.name}: score={player.score}, rack={rack_letters}")
    print()


def main() -> None:
    dictionary = PickleDictionary.from_pickle("NWL2023.pickle")

    game = ScrabbleGame(
        config=DEFAULT_CONFIG,
        player_names=["Alice", "Bob"],
        dictionary=dictionary,
        rng_seed=42,
    )

    state = game.get_state()

    # Force a predictable rack for demo purposes
    state.players[0].rack.tiles = [
        Tile("C", 3),
        Tile("A", 1),
        Tile("T", 1),
        Tile("S", 1),
        Tile("E", 1),
        Tile("D", 2),
        Tile("B", 3),
    ]

    print("Initial state")
    print_board(state.board)
    print_scores(state)

    move = PlayMove(placements=(
        Placement(row=7, col=7, tile_index_in_rack=0),
        Placement(row=7, col=8, tile_index_in_rack=1),
        Placement(row=7, col=9, tile_index_in_rack=2),
    ))

    validation = game.validate_move(move)
    print("Validation result:")
    print(f"valid={validation.valid}")
    print(f"errors={validation.errors}")
    print(f"words_formed={validation.words_formed}")
    print()

    result = game.apply_move(move)
    print("After move:")
    print(f"score_delta={result.score_delta}")
    print(f"words_formed={result.words_formed}")
    print(f"errors={result.errors}")
    print()

    new_state = game.get_state()
    print_board(new_state.board)
    print_scores(new_state)


if __name__ == "__main__":
    main()