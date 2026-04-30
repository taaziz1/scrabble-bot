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
        elif len(rack) > 0:
            for letter in rack:
                if letter in arc.final_letters:
                    if pos <= 0:
                        words.add(letter + word)
                    else:
                        words.add(word + letter)
                if arc.destination.arc_exists(letter):
                    c = rack.copy()
                    c.remove(letter)
                    go_on(pos, letter, word, c, arc.destination.outgoing_arcs[letter])
        elif Path.DELIMITER in arc.final_letters:
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
    total_words = 0
    loop_start = perf_counter()

    for _ in range(1000):
        r = choices(uppercase_letters, k=7)
        final = set()
        words = set()
        gen(0, "", r, g.root_arc)
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
    loop_end = perf_counter()
    print(f"generated {total_words} moves in {loop_end - loop_start} seconds")

    assert match