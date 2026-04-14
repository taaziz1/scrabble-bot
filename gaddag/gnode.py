from garc import Arc
from gpath import Path

from itertools import zip_longest

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