from .board import Board
from gaddag.GADDAG import GADDAG, Path


class CrossSets:
    def __init__(self, gaddag: GADDAG) -> None:
        self.GADDAG = gaddag
        self.valid_chars = set([chr(i) for i in range(ord('A'), ord('Z') + 1)])
        self.row_cross_sets = [[set() for _ in range(15)] for _ in range(15)]
        self.col_cross_sets = [[set() for _ in range(15)] for _ in range(15)]
        self.anchor_squares = {(7, 7)}
        self.row_cross_sets[7][7] = self.valid_chars.copy()
        self.col_cross_sets[7][7] = self.valid_chars.copy()

    def update_cross_sets(self, board, positions, already_placed):
        adjacent_positions = set()
        neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for position in positions:
            self.row_cross_sets[position.row][position.col] = set()
            self.col_cross_sets[position.row][position.col] = set()
            self.anchor_squares.discard((position.row, position.col))
            for n in neighbors:
                try:
                    row, col = position.row + n[0], position.col + n[1]
                    if board.is_empty_at(row, col):
                        adjacent_positions.add((row, col))
                except IndexError:
                    pass

        for placed in already_placed:
            for n in neighbors:
                try:
                    row, col = placed[0] + n[0], placed[1] + n[1]
                    if board.is_empty_at(row, col):
                        adjacent_positions.add((row, col))
                except IndexError:
                    pass

        self.anchor_squares.update(adjacent_positions)

        for adj_pos in adjacent_positions:
            row, col = adj_pos[0], adj_pos[1]
            row_cross_set = self.valid_chars.copy()
            col_cross_set = self.valid_chars.copy()

            # row check
            r = board.get_row(row)
            if col != 0 and r[col - 1] and col != 14 and r[col + 1]:
                accepted_letters = set()
                idx = col - 1
                node = self.GADDAG.root
                while idx != -1 and r[idx]:
                    node = node.follow_arc(r[idx])
                    idx -= 1
                if Path.DELIMITER in node.outgoing_arcs:
                    node = node.follow_arc(Path.DELIMITER)
                    start_pos = col + 1
                    for letter in node.outgoing_arcs:
                        idx = start_pos
                        arc = node.outgoing_arcs[letter]
                        while idx != 14 and r[idx+1] and r[idx] in arc.destination.outgoing_arcs:
                            arc = arc.destination.outgoing_arcs[r[idx]]
                            idx += 1

                        if (idx == 14 or not r[idx+1]) and r[idx] in arc.final_letters:
                            accepted_letters.add(letter)

                row_cross_set = row_cross_set & accepted_letters
            else:
                if col != 0 and r[col - 1]:
                    idx = col - 1
                    node = self.GADDAG.root
                    while idx != -1 and r[idx]:
                        node = node.follow_arc(r[idx])
                        idx -= 1
                    if Path.DELIMITER in node.outgoing_arcs:
                        row_cross_set = row_cross_set & node.outgoing_arcs[Path.DELIMITER].final_letters
                    else:
                        row_cross_set = set()

                if col != 14 and r[col + 1]:
                    idx = col + 1
                    node = self.GADDAG.root
                    accepted_letters = set()
                    word = ""
                    while idx != 15 and r[idx]:
                        word += r[idx]
                        idx += 1
                    for i in range(len(word) - 1, -1, -1):
                        node = node.follow_arc(word[i])
                    for letter in node.outgoing_arcs:
                        if Path.DELIMITER in node.outgoing_arcs[letter].final_letters:
                            accepted_letters.add(letter)
                    row_cross_set = row_cross_set & accepted_letters

            # column check
            c = board.get_col(col)
            if row != 0 and c[row - 1] and row != 14 and c[row + 1]:
                accepted_letters = set()
                idx = row - 1
                node = self.GADDAG.root
                while idx != -1 and c[idx]:
                    node = node.follow_arc(c[idx])
                    idx -= 1
                if Path.DELIMITER in node.outgoing_arcs:
                    node = node.follow_arc(Path.DELIMITER)
                    start_pos = row + 1
                    for letter in node.outgoing_arcs:
                        idx = start_pos
                        arc = node.outgoing_arcs[letter]
                        while idx != 14 and c[idx+1] and c[idx] in arc.destination.outgoing_arcs:
                            arc = arc.destination.outgoing_arcs[c[idx]]
                            idx += 1

                        if (idx == 14 or not c[idx+1]) and c[idx] in arc.final_letters:
                            accepted_letters.add(letter)

                col_cross_set = col_cross_set & accepted_letters
            else:
                if row != 0 and c[row - 1]:
                    idx = row - 1
                    node = self.GADDAG.root
                    while idx != -1 and c[idx]:
                        node = node.follow_arc(c[idx])
                        idx -= 1
                    if Path.DELIMITER in node.outgoing_arcs:
                        col_cross_set = col_cross_set & node.outgoing_arcs[Path.DELIMITER].final_letters
                    else:
                        col_cross_set = set()

                if row != 14 and c[row + 1]:
                    idx = row + 1
                    node = self.GADDAG.root
                    accepted_letters = set()
                    word = ""
                    while idx != 15 and c[idx]:
                        word += c[idx]
                        idx += 1
                    for i in range(len(word) - 1, -1, -1):
                        node = node.follow_arc(word[i])
                    for letter in node.outgoing_arcs:
                        if Path.DELIMITER in node.outgoing_arcs[letter].final_letters:
                            accepted_letters.add(letter)
                    col_cross_set = col_cross_set & accepted_letters

            self.row_cross_sets[row][col] = row_cross_set
            self.col_cross_sets[row][col] = col_cross_set

        print([(a, self.row_cross_sets[a[0]][a[1]], self.col_cross_sets[a[0]][a[1]]) for a in self.anchor_squares])
        print(len(self.anchor_squares))

    def is_anchor(self, row, column, transposed):
        if transposed:
            return (column, row) in self.anchor_squares
        return (row, column) in self.anchor_squares

    def valid_letter(self, row, column, letter, transposed):
        if self.is_anchor(row, column, transposed):
            if transposed:
                if letter in self.row_cross_sets[column][row]:
                    return True
            else:
                if letter in self.col_cross_sets[row][column]:
                    return True
            return False
        return True