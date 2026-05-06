import pickle
import time

from gaddag.GADDAG import GADDAG
from scrabble_game.config import DEFAULT_CONFIG
from scrabble_game.dictionary import PickleDictionary
from scrabble_game.game import ScrabbleGame
from scrabble_game.move import Placement, PlayMove, ExchangeMove, PassMove
from scrabble_game.results import MoveResult


class InteractiveGame:
    def __init__(self, lexicon, gaddag, players, config) -> None:
        self.dictionary = PickleDictionary.from_pickle(lexicon)

        print("loading...")

        self.g = None
        try:
            self.g = pickle.load(open(gaddag, "rb"))
        except FileNotFoundError:
            print(f"could not find {gaddag}")

        self.game = ScrabbleGame(
            config=config,
            player_names=players,
            dictionary=self.dictionary,
            gaddag=self.g
        )

        self.state = self.game.get_state()

        print("loaded!")

    def create_gaddag(self, dictionary: str, output: str) -> None:
        nwl2023 = pickle.load(open(dictionary, "rb"))

        g = GADDAG(nwl2023)
        pickle.dump(g, open(output, "wb"))

    def print_board(self) -> None:
        print(self.state.board)
        print()

    def print_scores(self) -> None:
        for player in self.state.players:
            rack_letters = [tile.letter for tile in player.rack]
            print(f"{player.name}: score={player.score}, rack={rack_letters}")
        print()

    def print_current_player(self) -> None:
        player_name = self.state.players[self.state.current_player_index].name
        print(f"{player_name}'s turn")

    def print_errors(self, result: MoveResult) -> None:
        for e in result.errors:
            print(e)
        print()

    def play_move(self, r: list[str]) -> None:
        already_placed = []
        tiles_to_place = []
        while not tiles_to_place:
            move = input("Enter starting tile row and column, direction (R or D), and word: ")

            rack = r.copy()

            move_args = move.split(' ')

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
                    if self.state.board.is_empty_at(row, column):
                        if letter in rack:
                            idx = rack.index(letter)
                            rack[idx] = ''
                            temp_tiles.append(Placement(row=row,
                                                        col=column,
                                                        tile_index_in_rack=idx))
                        elif '_' in rack:
                            idx = rack.index('_')
                            rack[idx] = ''
                            temp_tiles.append(Placement(row=row,
                                                        col=column,
                                                        tile_index_in_rack=idx,
                                                        assigned_letter=letter))
                        else:
                            success = False
                            print(f"don't have {letter} for {row} {column}")
                            break
                    elif self.state.board.get_tile(row, column).letter != letter:
                        success = False
                        print(f"{self.state.board.get_tile(row, column).letter} != {letter}")
                        break
                    else:
                        already_placed.append((row, column))
                    if direction == 'R':
                        column += 1
                    else:
                        row += 1
                if success:
                    tiles_to_place = temp_tiles
                else:
                    print('word cannot be formed with current tiles')
                    already_placed = []

        move = PlayMove(placements=tuple(tiles_to_place), already_placed=already_placed)
        result = self.game.apply_move(move)
        self.print_errors(result)

    def exchange_move(self, r) -> None:
        indices = []

        while not indices:
            rack = r.copy()
            letters = input('Enter the letters you would like to exchange, separated by spaces: ')
            t = letters.split(' ')

            for letter in t:
                if letter not in rack:
                    print(f"{letter} not in rack")
                    indices.clear()
                    break
                idx = rack.index(letter)
                indices.append(idx)
                rack[idx] = ''

        move = ExchangeMove(tuple(indices))
        result = self.game.apply_move(move)
        self.print_errors(result)

    def pass_move(self) -> None:
        result = self.game.apply_move(PassMove())
        self.print_errors(result)

    def gen_moves(self, r: list[str]) -> str:
        start = time.perf_counter()
        moves = self.game.potential_moves(r)
        end = time.perf_counter()
        print(f"generated and validated moves in {end - start} seconds")
        return moves

    def start(self) -> None:
        self.print_board()
        self.print_current_player()
        self.print_scores()

        while not self.state.is_finished:
            r = [tile.letter for tile
                 in self.state.players[self.state.current_player_index].rack.as_list()]
            move_type = ""

            while move_type != 'place' and move_type != 'exchange' and move_type != 'pass':
                move_type = input("Enter 'place' to play tiles, 'exchange' to exchange tiles, 'pass' to pass, or 'gen' to generate potential moves: ")
                if move_type == 'gen':
                    print(self.gen_moves(r))

            if move_type == "place":
                self.play_move(r)
            elif move_type == "exchange":
                self.exchange_move(r)
            else:
                self.pass_move()

            self.state = self.game.get_state()
            self.print_board()
            self.print_scores()
            self.print_current_player()

        print(f"{self.state.players[self.state.winner_index].name} wins!")


if __name__ == "__main__":
    dictionary_name = "NWL2023.pickle"
    gaddag_name = "gaddagNWL2023-2.pickle"
    player_names = ["Player 1", "Player 2"]
    conf = DEFAULT_CONFIG

    ig = InteractiveGame(dictionary_name, gaddag_name, player_names, conf)
    ig.start()