import pickle
import time
from dataclasses import dataclass

from gaddag.GADDAG import GADDAG
from scrabble_game.config import DEFAULT_CONFIG, GameConfig
from scrabble_game.dictionary import PickleDictionary
from scrabble_game.game import ScrabbleGame
from scrabble_game.move import Placement, PlayMove, ExchangeMove, PassMove
from scrabble_game.results import MoveResult


@dataclass
class Player:
    name: str
    computer: bool=False

    def __str__(self):
        return self.name


class InteractiveGame:
    def __init__(self, lexicon: str, gaddag: str | GADDAG,
                 humans: list[Player], config: GameConfig, bots: list[Player]=None) -> None:
        self.dictionary = PickleDictionary.from_pickle(lexicon)

        self.g = None
        if isinstance(gaddag, GADDAG):
            self.g = gaddag
        else:
            print(f"loading {gaddag}...")
            try:
                self.g = pickle.load(open(gaddag, "rb"))
                print(f"loaded {gaddag} successfully!")
            except FileNotFoundError:
                print(f"could not find {gaddag}")

        self.players = humans
        if bots:
            self.players.extend(bots)
        p_names = list(map(str, self.players))

        self.game = ScrabbleGame(
            config=config,
            player_names=p_names,
            dictionary=self.dictionary,
            gaddag=self.g
        )

        self.state = self.game.get_state()

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

    def print_errors(self, result: MoveResult) -> bool:
        error_found = False
        for e in result.errors:
            print(e)
            error_found = True
        if error_found:
            print()
        return error_found

    def play_move(self, r: list[str], move: str) -> PlayMove | None:
        already_placed = []
        tiles_to_place = []
        rack = r.copy()
        move_args = move.split(' ')

        if len(move_args) != 4:
            print(f"got {len(move_args)} arguments, expected 4 arguments")
            return None

        direction = move_args[2]
        word = list(move_args[3])

        try:
            row, col = int(move_args[0]) - 1, move_args[1]
            column = ord(col) - ord('A')
            if row < 0 or row > 14 or column < 0 or column > 14:
                print("row or column invalid")
                return None

        except ValueError:
            print('invalid row or column number')
            return None

        except TypeError:
            print('invalid row or column number')
            return None

        if direction != 'R' and direction != 'D':
            print('invalid direction, choose \'R\' or \'D\'')
            return None

        for letter in word:
            if self.state.board.is_empty_at(row, column):
                if letter in rack:
                    idx = rack.index(letter)
                    rack[idx] = ''
                    tiles_to_place.append(Placement(row=row,
                                                col=column,
                                            tile_index_in_rack=idx))
                elif '_' in rack:
                    idx = rack.index('_')
                    rack[idx] = ''
                    tiles_to_place.append(Placement(row=row,
                                                col=column,
                                                tile_index_in_rack=idx,
                                                assigned_letter=letter))
                else:
                    print(f"don't have {letter} for {row} {column}")
                    return None
            elif self.state.board.get_tile(row, column).letter != letter:
                print(f"'{self.state.board.get_tile(row, column).letter}' "
                      f"differs from placed tile: '{letter}', at {row} {column}")
                return None
            else:
                already_placed.append((row, column))
            if direction == 'R':
                column += 1
            else:
                row += 1

        return PlayMove(placements=tuple(tiles_to_place), already_placed=already_placed)

    def exchange_move(self, r: list[str], letters: str) -> ExchangeMove | None:
        indices = []
        rack = r.copy()
        t = letters.split(' ')

        if len(t) <= 0:
            return None

        for letter in t:
            if letter not in rack:
                print(f"{letter} not in rack")
                return None
            idx = rack.index(letter)
            indices.append(idx)
            rack[idx] = ''
        return ExchangeMove(tuple(indices))

    def pass_move(self) -> MoveResult:
        return self.game.apply_move(PassMove())

    def gen_moves(self, r: list[str]) -> str:
        moves = self.game.potential_moves(r)
        return moves

    def start(self) -> None:
        self.print_board()
        self.print_current_player()
        self.print_scores()

        while not self.state.is_finished:
            r = [tile.letter for tile
                 in self.state.players[self.state.current_player_index].rack.as_list()]
            move_type = ""

            if self.players[self.state.current_player_index].computer:
                generated_moves = self.gen_moves(r)
                if generated_moves:
                    best_move = ' '.join(map(str, generated_moves[0][0]))
                    move = self.play_move(r, best_move)
                    result = self.game.apply_move(move)
                    self.print_errors(result)
                else:
                    self.pass_move()
            else:
                while move_type != 'place' and move_type != 'exchange' and move_type != 'pass':
                    move_type = input("Enter 'place' to play tiles, 'exchange' to exchange tiles, or 'pass' to pass: ")
                    if move_type == 'gen':
                        start = time.perf_counter()
                        print(self.gen_moves(r))
                        end = time.perf_counter()
                        print(f"generated and validated moves in {end - start} seconds")

                if move_type == "place":
                    move = None
                    while not move:
                        play = input("Enter starting tile row and column, direction (R or D), and word: ")
                        move = self.play_move(r, play)
                    result = self.game.apply_move(move)
                    self.print_errors(result)
                elif move_type == "exchange":
                    move = None
                    while not move:
                        letters = input('Enter the letters you would like to exchange, separated by spaces: ')
                        move = self.exchange_move(r, letters)
                    result = self.game.apply_move(move)
                    self.print_errors(result)
                else:
                    result = self.pass_move()
                    self.print_errors(result)

            self.state = self.game.get_state()
            self.print_board()
            self.print_scores()
            self.print_current_player()

        print(f"{self.state.players[self.state.winner_index].name} wins!")


if __name__ == "__main__":
    dictionary_name = "NWL2023.pickle"
    gaddag_name = "gaddagNWL2023-2.pickle"
    player_names = [Player("Player 1")]
    computer_names = [Player("Computer 1", True)]
    conf = DEFAULT_CONFIG

    ig = InteractiveGame(dictionary_name, gaddag_name, player_names, conf, computer_names)
    ig.start()