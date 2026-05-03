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

def print_current_player(state) -> None:
    player_name = state.players[state.current_player_index].name
    print(f"{player_name}'s turn")


def main() -> None:
    dictionary = PickleDictionary.from_pickle("NWL2023.pickle")

    game = ScrabbleGame(
        config=DEFAULT_CONFIG,
        player_names=["Player 1", "Player 2"],
        dictionary=dictionary,
    )

    state = game.get_state()

    print_board(state.board)
    print_current_player(state)
    print_scores(state)

    while not state.is_finished:
        tiles_to_place = []
        move = PassMove()
        move_type = ""

        while move_type != 'place' and move_type != 'exchange' and move_type != 'pass':
            move_type = input("Enter 'place' to play tiles, 'exchange' to exchange tiles, or 'pass' to pass: ")

        if move_type == "place":
            while not tiles_to_place:
                move = input("Enter starting tile row and column, direction (R or D), and word: ")

                move_args = move.split(' ')
                rack = [tile.letter for tile in state.players[state.current_player_index].rack.as_list()]

                if len(move_args) == 4:
                    direction = move_args[2]
                    word = list(move_args[3])
                    try:
                        row, col = int(move_args[0]) - 1, move_args[1]
                        column = ord(col) - ord('A')
                        if row < 0 or row > 14 or column < 0 or column > 14:
                            print("row or column invalid")
                            continue
                    except ValueError:
                        print('invalid row or column number')
                        continue
                    except TypeError:
                        print('invalid row or column number')
                        continue

                    if direction != 'R' and direction != 'D':
                        print('invalid direction, choose \'R\' or \'D\'')
                        continue

                    success = True
                    temp_tiles = []
                    for letter in word:
                        if state.board.is_empty_at(row, column):
                            if letter in rack:
                                idx = rack.index(letter)
                                rack[idx] = ''
                                temp_tiles.append(Placement(row=row,
                                                                col=column,
                                                                tile_index_in_rack=idx))
                            else:
                                success = False
                                break
                        elif state.board.get_tile(row, column).letter != letter:
                            success = False
                            break
                        if direction == 'R':
                            column += 1
                        else:
                            row += 1
                    if success:
                        tiles_to_place = temp_tiles
                    else:
                        print('word cannot be formed with current tiles')


            move = PlayMove(placements=tuple(tiles_to_place))

        elif move_type == "exchange":
            rack = [tile.letter for tile in state.players[state.current_player_index].rack.as_list()]
            indices = []

            while not indices:
                letters = input('Enter the letters you would like to exchange, separated by spaces: ')
                t = letters.split(' ')
                success = True

                for letter in t:
                    if letter not in rack:
                        print(f"{letter} not in rack")
                        success = False
                        break
                    idx = rack.index(letter)
                    indices.append(idx)
                    rack[idx] = ''

                if not success:
                    continue

            move = ExchangeMove(tuple(indices))

        result = game.apply_move(move)

        state = game.get_state()
        print_board(state.board)

        for e in result.errors:
            print(e)
        print()
        print_scores(state)
        print_current_player(state)

if __name__ == "__main__":
    main()