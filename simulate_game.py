from play_interactive import InteractiveGame
from scrabble_game.config import DEFAULT_CONFIG

if __name__ == "__main__":
    dictionary_name = "NWL2023.pickle"
    gaddag_name = "gaddagNWL2023-2.pickle"
    player_names = ["Player 1", "Player 2"]
    conf = DEFAULT_CONFIG

    for _ in range(100):

        ig = InteractiveGame(dictionary_name, gaddag_name, player_names, conf)
        print()

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
            print(f"\rat move {move_number}", end="", flush=True)
            ig.state = ig.game.get_state()

        print(f"\ngame finished with {move_number} moves:")
        ig.print_board()
        ig.print_scores()
        print(f"{ig.state.players[ig.state.winner_index].name} wins!")