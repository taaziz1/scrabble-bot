from gword import Word

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