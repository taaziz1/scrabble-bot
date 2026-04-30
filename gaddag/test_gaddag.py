from random import choices
from time import perf_counter
from GADDAG import Path, GADDAG
from pickle import load
from itertools import chain, combinations, permutations

def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, x) for x in range(len(s) + 1))

nwl2023 = load(open("../NWL2023.pickle", "rb"))

start1 = perf_counter()
g = load(open("../gaddagNWL2023.pickle", "rb"))
end1 = perf_counter()

print(f"loaded in {end1 - start1} seconds")


def test_1000_variations():
    row = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
    anchor = 6

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
                            if pos <= 0:
                                words.add(letter + word)
                            else:
                                words.add(word + letter)
                        if arc.destination.arc_exists(letter):
                            rack['size'] -= 1
                            rack[letter] -= 1
                            go_on(pos, letter, word, rack, arc.destination.outgoing_arcs[letter])
                            rack[letter] += 1
                            rack['size'] += 1
            if Path.DELIMITER in arc.final_letters:
                words.add(word)

    def go_on(pos, L, word, rack, new_arc):
        if pos <= 0:
            new_word = L + word
            if anchor - pos > 0 and not row[anchor + pos - 1]:
                gen(pos - 1, new_word, rack, new_arc)
            if (anchor - pos == 0 or not row[anchor - pos - 1]) and anchor < 14 and not row[
                anchor + 1] and new_arc.destination.arc_exists(Path.DELIMITER):
                gen(1, new_word, rack, new_arc.destination.outgoing_arcs[Path.DELIMITER])
        else:
            new_word = word + L
            if anchor + pos < 14:
                gen(pos + 1, new_word, rack, new_arc)

    uppercase_letters = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    match = True
    rack_size = 7
    total_words = 0
    counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0,
              'F': 0, 'G': 0, 'H': 0, 'I': 0, 'J': 0,
              'K': 0, 'L': 0, 'M': 0, 'N': 0, 'O': 0,
              'P': 0, 'Q': 0, 'R': 0, 'S': 0, 'T': 0,
              'U': 0, 'V': 0, 'W': 0, 'X': 0, 'Y': 0,
              'Z': 0, 'size': 0}

    loop_start = perf_counter()

    for _ in range(10000):
        r = choices(uppercase_letters, k=rack_size)

        for letter in r:
            counts[letter] += 1
        counts['size'] = rack_size

        final = set()
        words = set()
        gen(0, "", counts, g.root_arc)
        for letters in powerset(r):
            for p in permutations(letters):
                candidate = ''.join(p)
                if candidate in nwl2023:
                    final.add(candidate)
        total_words += len(words)
        if final != words:
            print(final)
            print(words)
            match = False
            break
        for letter in counts:
            counts[letter] = 0
    loop_end = perf_counter()
    print(f"generated {total_words} moves in {loop_end - loop_start} seconds")

    assert match