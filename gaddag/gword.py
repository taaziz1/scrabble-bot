from gpath import Path

class Word:
    def __init__(self, letters):
        self.letters = letters

    def __str__(self):
        return ''.join(self.letters)

    def __eq__(self, other):
        return self.letters == other.letters

    def to_delimited_paths(self):
        paths = []
        for index in range(1, len(self.letters) - 1):
            reversed_prefix = self.letters[0:index][::-1]
            suffix = self.letters[index:]
            paths.append(Path(reversed_prefix + [Path.DELIMITER] + suffix))
        return paths