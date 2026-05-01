from GADDAG import GADDAG, Path
import pickle
import time

# start1 = time.perf_counter()
# g = pickle.load(open("../gaddagNWL2023.pickle", "rb"))
# end1 = time.perf_counter()
#
# print(f"loaded in {end1 - start1} seconds")

g = GADDAG(['BAGUETTE', 'GETTABLE'])

# print([''.join(p.letters) for p in g.root.final_paths()])

# nwl2023 = pickle.load(open("../NWL2023.pickle", "rb"))
#
# startGAD = time.perf_counter()
# g = GADDAG(nwl2023)
# pickle.dump(g, open("../gaddagNWL2023.pickle", "wb"))
# endGAD = time.perf_counter()
#
# print(f"created in {endGAD - startGAD} seconds")


# start2 = time.perf_counter()
# print(g.find("NESSES"))
# end2 = time.perf_counter()
# print(f"found in {end2 - start2} seconds")

r = {'A': 1, 'B': 1, 'C': 0, 'D': 0, 'E': 2,
          'F': 0, 'G': 0, 'H': 0, 'I': 0, 'J': 0,
          'K': 0, 'L': 0, 'M': 0, 'N': 0, 'O': 0,
          'P': 0, 'Q': 0, 'R': 0, 'S': 0, 'T': 2,
          'U': 0, 'V': 0, 'W': 0, 'X': 0, 'Y': 0,
          'Z': 0, 'blank': 1, 'size': 7}
row = [None, None, None, None, None, None, None, 'G', None, None, None, None, None, None, None]
anchor = 8
words = []


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
                            words.append(letter + word)
                        elif anchor + pos == 14 or not row[anchor + pos + 1]:
                            words.append(word + letter)
                    if letter == 'blank':
                        rack['size'] -= 1
                        rack['blank'] -= 1
                        for l in arc.final_letters:
                            if not l == Path.DELIMITER:
                                if pos <= 0 and (anchor - pos == 0 or not row[anchor - pos - 1]):
                                    words.append(l.lower() + word)
                                elif anchor + pos == 14 or not row[anchor + pos + 1]:
                                    words.append(word + l.lower())
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
            words.append(word + Path.DELIMITER)

def go_on(pos, L, word, rack, new_arc):
    if pos <= 0:
        new_word = L + word
        if anchor + pos > 0:
            gen(pos - 1, new_word, rack, new_arc)
        if ((anchor + pos == 0 or not row[anchor + pos - 1]) and anchor < 14
                and new_arc.destination.arc_exists(Path.DELIMITER)):
            gen(1, new_word + Path.DELIMITER, rack, new_arc.destination.outgoing_arcs[Path.DELIMITER])
    else:
        new_word = word + L
        if anchor + pos < 14:
            gen(pos + 1, new_word, rack, new_arc)

start2 = time.perf_counter()
gen(0, "", r, g.root_arc)
end2 = time.perf_counter()

print(f"found {len(words)} words in {end2 - start2} seconds")

print(words)

exit(0)


