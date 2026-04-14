from gpath import Path

class Arc:
    def __init__(self, destination: Node):
        self.destination = destination
        self.final_letters = set()

    def __eq__(self, other):
        return self.destination == other.destination and self.final_letters == other.final_letters

    def add_final_letter(self, letter):
        self.final_letters.add(letter)

    def final_paths(self):
        return [Path([f1]) for f1 in self.final_letters] + self.destination.final_paths()