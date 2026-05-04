from itertools import zip_longest


class GADDAG:
    def __init__(self, words = None):
        self.root = Node()
        self.root_arc = Arc(self.root)
        if words:
            for word in words:
                self.add(word)

    def add(self, word):
        chars = list(word)
        self.root.create_final_path(chars[::-1] + [Path.DELIMITER])

        for path in Word(chars).to_delimited_paths():
            self.root.create_final_path(path.letters)

        return self

    def find(self, substring):
        if len(substring) < 2:
            return
        first_letter, second_letter, *last_letters = list(substring)
        words = set()
        rev = last_letters[::-1]

        if not self.root.path_exists(rev):
            return words

        for path in self.root.follow_path(rev).final_paths():
            if path.starts_with([second_letter, first_letter]):
                words.add(str(Path(rev + path.letters).to_word()))

        return words

    def generate_moves(self, board, cross_sets, rack_tiles):
        moves = set()
        words = set()
        row = []
        anchor = -1
        transposed = False
        idx = -1

        def gen(pos, word, rack, arc):
            if row[anchor + pos]:
                letter = row[anchor + pos]
                if arc.destination.arc_exists(letter):
                    go_on(pos, letter, word, rack, arc.destination.outgoing_arcs[letter])
            else:
                if rack['size'] > 0:
                    for letter in rack:
                        if rack[letter] > 0:
                            if letter in arc.final_letters:
                                if pos <= 0 and (anchor + pos == 0 or not row[anchor + pos - 1]):
                                    words.add((anchor, idx, letter + word))
                                elif ((anchor + pos == 14 or not row[anchor + pos + 1])
                                      and cross_sets.valid_letter(idx, anchor + pos, letter, transposed)):
                                    words.add((anchor, idx, word + letter))
                            if letter == '_':
                                rack['size'] -= 1
                                rack['_'] -= 1
                                for l in arc.final_letters:
                                    if not l == Path.DELIMITER:
                                        if pos <= 0 and (anchor + pos == 0 or not row[anchor + pos - 1]):
                                            words.add((anchor, idx, l.lower() + word))
                                        elif ((anchor + pos == 14 or not row[anchor + pos + 1])
                                              and cross_sets.valid_letter(idx, anchor + pos, l, transposed)):
                                            words.add((anchor, idx, word + l.lower()))
                                for l, a in arc.destination.outgoing_arcs.items():
                                    if (not l == Path.DELIMITER
                                            and cross_sets.valid_letter(idx, anchor + pos, l, transposed)):
                                        go_on(pos, l.lower(), word, rack, a)
                                rack['_'] += 1
                                rack['size'] += 1
                            elif (arc.destination.arc_exists(letter)
                                  and cross_sets.valid_letter(idx, anchor + pos, letter, transposed)):
                                rack['size'] -= 1
                                rack[letter] -= 1
                                go_on(pos, letter, word, rack, arc.destination.outgoing_arcs[letter])
                                rack[letter] += 1
                                rack['size'] += 1
                if (Path.DELIMITER in arc.final_letters
                        and cross_sets.valid_letter(idx, anchor + pos + 1, word[-1:], transposed)):
                    words.add((anchor, idx, word + Path.DELIMITER))

        def go_on(pos, L, word, rack, new_arc):
            if pos <= 0:
                new_word = L + word
                if pos == 0 or not cross_sets.is_anchor(idx, anchor + pos, transposed):
                    if anchor + pos > 0:
                        gen(pos - 1, new_word, rack, new_arc)
                    if ((anchor + pos == 0 or not row[anchor + pos - 1]) and anchor < 14
                            and new_arc.destination.arc_exists(Path.DELIMITER)):
                        gen(1, new_word + Path.DELIMITER, rack, new_arc.destination.outgoing_arcs[Path.DELIMITER])
            else:
                new_word = word + L
                if anchor + pos < 14:
                    gen(pos + 1, new_word, rack, new_arc)

        # convert rack set to dictionary
        r = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0,
             'F': 0, 'G': 0, 'H': 0, 'I': 0, 'J': 0,
             'K': 0, 'L': 0, 'M': 0, 'N': 0, 'O': 0,
             'P': 0, 'Q': 0, 'R': 0, 'S': 0, 'T': 0,
             'U': 0, 'V': 0, 'W': 0, 'X': 0, 'Y': 0,
             'Z': 0, '_': 0, 'size': 0}

        for tile in rack_tiles:
            r[tile] += 1
            r['size'] += 1

        final_moves = set()
        # generate row moves
        for a in cross_sets.anchor_squares:
            idx = a[0]
            row = board.get_row(idx)
            words = set()
            anchor = a[1]
            gen(0, "", r.copy(), self.root_arc)
            moves.update(words)
        for move in moves:
            delim = move[2].index(Path.DELIMITER) - 1
            row_num = move[1] + 1
            col_char = chr(move[0] - delim + ord('A'))
            final_moves.add((row_num, col_char, 'R', move[2].replace(Path.DELIMITER, '')))
        moves.clear()

        # generate column moves
        transposed = True
        for a in cross_sets.anchor_squares:
            idx = a[1]
            row = board.get_col(idx)
            words = set()
            anchor = a[0]
            gen(0, "", r.copy(), self.root_arc)
            moves.update(words)
        for move in moves:
            delim = move[2].index(Path.DELIMITER) - 1
            row_num = move[0] - delim + 1
            col_char = chr(move[1] + ord('A'))
            final_moves.add((row_num, col_char, 'D', move[2].replace(Path.DELIMITER, '')))

        return sorted(final_moves, key=lambda mv: len(mv[3]), reverse=True)


class Node:
    def __init__(self):
        self.outgoing_arcs = {}

    def __eq__(self, other):
        return self.outgoing_arcs == other.outgoing_arcs

    def create_arc(self, letter, destination=None):
        if letter in self.outgoing_arcs:
            return self.outgoing_arcs[letter]
        if destination is None:
            destination = Node()
        a = Arc(destination)
        self.outgoing_arcs[letter] = a
        return a

    def arc_exists(self, letter):
        return letter in self.outgoing_arcs

    def create_final_arc(self, letter, final_letter, destination = None):
        if destination is None:
            destination = Node()
        a = self.create_arc(letter, destination)
        a.add_final_letter(final_letter)
        return a

    def create_path(self, letters, destinations = None):
        destinations = destinations or []
        node = self

        for letter, destination in zip_longest(letters, destinations):
            if letter is None:
                break
            node = node.create_arc(letter, destination or Node()).destination
        return node

    def path_exists(self, letters):
        node = self

        for letter in letters:
            if not node.arc_exists(letter):
                return False
            node = node.follow_arc(letter)
        return True

    def create_final_path(self, letters, destinations = None):
        destinations = destinations or []
        if len(letters) < 2:
            return
        *initial_letters, second_last_letter, last_letter = letters
        second_last_node = self.create_path(initial_letters, destinations)

        final_node = Node()
        if len(destinations) > len(initial_letters):
            final_node = destinations[len(initial_letters)]
        second_last_node.create_final_arc(second_last_letter, last_letter, final_node)

    def final_path_exists(self, letters):
        *initial_letters, second_last_letter, last_letter = letters

        if not self.path_exists(initial_letters):
            return False
        desired_final_path = Path([second_last_letter, last_letter])
        return any(final_path == desired_final_path
                   for final_path in self.follow_path(initial_letters).final_paths())

    def follow_arc(self, letter):
        return self.outgoing_arcs[letter].destination

    def follow_path(self, letters):
        node = self

        for letter in letters:
            node = node.follow_arc(letter)
        return node

    def final_paths(self):
        return [
            Path([letter_sym] + path.letters)
            for letter_sym, arc in self.outgoing_arcs.items()
            for path in arc.final_paths()
        ]


class Arc:
    def __init__(self, destination):
        self.destination = destination
        self.final_letters = set()

    def __eq__(self, other):
        return self.destination == other.destination and self.final_letters == other.final_letters

    def add_final_letter(self, letter):
        self.final_letters.add(letter)

    def final_paths(self):
        return [Path([fl]) for fl in self.final_letters] + self.destination.final_paths()


class Path:
    DELIMITER = '♢'

    def __init__(self, letters):
        self.letters = letters

    def __str__(self):
        return ' > '.join(self.letters)

    def __eq__(self, other):
        return self.letters == other.letters

    def reversed_prefix_letters(self):
        res = []
        for char in self.letters:
            if char == self.DELIMITER:
                break
            res.append(char)
        return res

    def suffix_letters(self):
        res = []
        if not self.includes_delimiter() or self.letters[-1] == self.DELIMITER:
            return res
        delimiter_found = False
        for char in self.letters:
            if delimiter_found:
                res.append(char)
            if char == self.DELIMITER:
                delimiter_found = True
        return res

    def includes_delimiter(self):
        return self.DELIMITER in self.letters

    def starts_with(self, letters):
        return ''.join(self.letters).startswith(''.join(letters))

    def to_word(self):
        return Word(self.reversed_prefix_letters()[::-1] + self.suffix_letters())


class Word:
    def __init__(self, letters):
        self.letters = letters

    def __str__(self):
        return ''.join(self.letters)

    def __eq__(self, other):
        return self.letters == other.letters

    def to_delimited_paths(self):
        paths = []
        for index in range(1, len(self.letters)):
            reversed_prefix = self.letters[0:index][::-1]
            suffix = self.letters[index:]
            paths.append(Path(reversed_prefix + [Path.DELIMITER] + suffix))
        return paths