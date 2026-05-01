from random import sample
from time import perf_counter
from GADDAG import Path, GADDAG
from pickle import load
from itertools import chain, combinations, permutations

def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, x) for x in range(len(s) + 1))


nwl2023 = load(open("NWL2023.pickle", "rb"))

start1 = perf_counter()
g = load(open("gaddagNWL2023.pickle", "rb"))
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
                            if pos <= 0 and (anchor - pos == 0 or not row[anchor - pos - 1]):
                                words.add(letter + word)
                            elif anchor + pos == 14 or not row[anchor + pos + 1]:
                                words.add(word + letter)
                        if letter == 'blank':
                            rack['size'] -= 1
                            rack['blank'] -= 1
                            for l in arc.final_letters:
                                if not l == Path.DELIMITER:
                                    if pos <= 0 and (anchor - pos == 0 or not row[anchor - pos - 1]):
                                        words.add(l.lower() + word)
                                    elif anchor + pos == 14 or not row[anchor + pos + 1]:
                                        words.add(word + l.lower())
                            for l, a in arc.destination.outgoing_arcs.items():
                                if not l == Path.DELIMITER:
                                    go_on(pos, l.lower(), word, rack, a)
                            rack['blank'] += 1
                            rack['size'] += 1
                        elif arc.destination.arc_exists(letter):
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
            if anchor + pos > 0:
                gen(pos - 1, new_word, rack, new_arc)
            if ((anchor + pos == 0 or not row[anchor + pos - 1]) and anchor < 14
                    and new_arc.destination.arc_exists(Path.DELIMITER)):
                gen(1, new_word, rack, new_arc.destination.outgoing_arcs[Path.DELIMITER])
        else:
            new_word = word + L
            if anchor + pos < 14:
                gen(pos + 1, new_word, rack, new_arc)

    bag = (
        ["A"] * 9 + ["B"] * 2 + ["C"] * 2 +
        ["D"] * 4 + ["E"] * 12 + ["F"] * 2 + ["G"] * 3 +
        ["H"] * 2 + ["I"] * 9 + ["J"] * 1 + ["K"] * 1 +
        ["L"] * 4 + ["M"] * 2 + ["N"] * 6 + ["O"] * 8 +
        ["P"] * 2 + ["Q"] * 1 + ["R"] * 6 + ["S"] * 4 +
        ["T"] * 6 + ["U"] * 4 + ["V"] * 2 + ["W"] * 2 +
        ["X"] * 1 + ["Y"] * 2 + ["Z"] * 1 + ["blank"] * 2
    )

    lowercase_letters = [chr(i) for i in range(ord('a'), ord('z') + 1)]

    match = True
    rack_size = 7
    total_words = 0
    counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0,
              'F': 0, 'G': 0, 'H': 0, 'I': 0, 'J': 0,
              'K': 0, 'L': 0, 'M': 0, 'N': 0, 'O': 0,
              'P': 0, 'Q': 0, 'R': 0, 'S': 0, 'T': 0,
              'U': 0, 'V': 0, 'W': 0, 'X': 0, 'Y': 0,
              'Z': 0, 'blank': 0, 'size': 0}

    total_time_elapsed = 0
    iterations = -1
    max_time = 0
    most_tedious_rack = []

    for _ in range(1000):
        iteration_start = perf_counter()
        r = sample(bag, k=rack_size)

        for letter in r:
            counts[letter] += 1
        counts['size'] = rack_size

        final = set()
        words = set()
        gen(0, "", counts, g.root_arc)
        for letters in powerset(r):
            for p in permutations(letters):
                candidates = [""]

                for c in p:
                    if c == 'blank':
                        candidates = [cand + letter for cand in candidates for letter in lowercase_letters]
                    else:
                        candidates = [cand + c for cand in candidates]
                for candidate in candidates:
                    if candidate.upper() in nwl2023:
                        final.add(candidate)
        total_words += len(words)
        if final != words:
            print(final)
            print(words)
            print(words - final)
            match = False
            break
        iteration_end = perf_counter()
        time_elapsed = iteration_end - iteration_start
        total_time_elapsed += time_elapsed
        if max_time < time_elapsed:
            max_time = time_elapsed
            most_tedious_rack = [i for i in counts.items() if i[1] > 0]
        iterations += 1
        for letter in counts:
            counts[letter] = 0
    iterations += 1

    print(f"\ngenerated {total_words} moves in {total_time_elapsed} seconds\n"
          f"longest iteration: {max_time} seconds, time per iteration: {total_time_elapsed / iterations} seconds\n"
          f"worst rack: {most_tedious_rack}")

    assert match