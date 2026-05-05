
COLUMNS = {
    1 : "A", 2 : "B", 3 : "C", 4 : "D", 5 : "E", 
    6 : "F", 7 : "G", 8 : "H", 9 : "I", 10 : "J", 
    11 : "K", 12 : "L", 13 : "M", 14 : "N", 15 : "O", 
}

def create_gcg_file(filename, p1, p2):
    with open(filename, 'w') as f:
        f.write(f"#player1 {p1}\n")
        f.write(f"#player2 {p2}\n")

def add_played_move(filename, player_name, rack, position, word, word_score, player_score, horizontal=True): 
    
    p = f"{position.row}{COLUMNS[position.col]}" if horizontal else f"{COLUMNS[position.col]}{position.row}"
    with open(filename, 'a') as f:
        f.write(f">{player_name}: {''.join(rack.as_list())} {p} {word} {word_score:+d} {player_score}\n")
    return

def add_exchanged_move(filename, player_name, rack, tiles_exchanged, player_score):
    with open(filename, 'a') as f:
        f.write(f">{player_name}: {''.join(rack.as_list())} -{tiles_exchanged} +0 {player_score}\n")
    return

def add_pass_move(filename, player_name, rack, player_score):
    with open(filename, 'a') as f:
        f.write(f">{player_name}: {''.join(rack.as_list())} - +0 {player_score}\n")
    return

def add_remainder_tiles(filename, player_name, tiles, value, player_score):
    with open(filename, 'a') as f:
        f.write(f">{player_name}: ({tiles}) {value:+d} {player_score}\n")
    return
