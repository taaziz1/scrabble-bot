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