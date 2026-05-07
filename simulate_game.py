import pickle

from play_interactive import InteractiveGame
from scrabble_game.config import DEFAULT_CONFIG

if __name__ == "__main__":
    dictionary_name = "NWL2023.pickle"
    gaddag_name = "gaddagNWL2023-2.pickle"
    player_names = ["Player 1", "Player 2"]
    conf = DEFAULT_CONFIG
    gaddag = pickle.load(open("gaddagNWL2023-2.pickle", "rb"))
    NUMBER_OF_GAMES = 10
    verbose = True

    for i in range(NUMBER_OF_GAMES):
        if verbose:
            print(f"{"—" * 12} Game {i+1} {"—" * 12}")
        else:
            print(f"\ron game {i+1}/{NUMBER_OF_GAMES}", end="", flush=True)

        ig = InteractiveGame(dictionary_name, gaddag, player_names, conf)

        move_number = 0
        while not ig.state.is_finished:
            r = [tile.letter for tile
                 in ig.state.players[ig.state.current_player_index].rack.as_list()]
            generated_moves = ig.gen_moves(r)
            if generated_moves:
                best_move = ' '.join(map(str, generated_moves[0][0]))
                move = ig.play_move(r, best_move)
                result = ig.game.apply_move(move)
                if ig.print_errors(result):
                    print(f"failed on {best_move} and rack {r} with board: ")
                    break
            else:
                ig.pass_move()
            move_number += 1
            if verbose:
                print(f"\rat move {move_number}", end="", flush=True)
            ig.state = ig.game.get_state()

        if verbose:
            print(f"\ngame finished with {move_number} moves:")
            ig.print_board()
            ig.print_scores()
            print(f"{ig.state.players[ig.state.winner_index].name} wins!\n")

    print(f"\nsimulated {NUMBER_OF_GAMES} games")