from play_interactive import InteractiveGame
from scrabble_game.config import DEFAULT_CONFIG

if __name__ == "__main__":
    dictionary_name = "NWL2023.pickle"
    gaddag_name = "gaddagNWL2023-2.pickle"
    player_names = ["Player 1", "Player 2"]
    conf = DEFAULT_CONFIG

    ig = InteractiveGame(dictionary_name, gaddag_name, player_names, conf)

    ig.print_board()
    ig.print_current_player()
    ig.print_scores()

    while not ig.state.is_finished:
        r = [tile.letter for tile
             in ig.state.players[ig.state.current_player_index].rack.as_list()]
        generated_moves = ig.gen_moves(r)
        if generated_moves:
            ig.play_move(r)
        else:
            ig.pass_move()

        ig.state = ig.game.get_state()
    ig.print_board()
    ig.print_scores()
    print(f"{ig.state.players[ig.state.winner_index].name} wins!")