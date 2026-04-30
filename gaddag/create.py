from GADDAG import GADDAG, Path
import pickle
import time

# start1 = time.perf_counter()
# g = pickle.load(open("../gaddagNWL2023.pickle", "rb"))
# end1 = time.perf_counter()
#
# print(f"loaded in {end1 - start1} seconds")

g = GADDAG(['BOOST'])

# print([''.join(p.letters) for p in g.root.final_paths()])

# nwl2023 = pickle.load(open("../NWL2023.pickle", "rb"))
#
# startGAD = time.perf_counter()
# g = GADDAG(s)
# pickle.dump(g, open("../gaddagNWL2023.pickle", "wb"))
# endGAD = time.perf_counter()
#
# print(f"created in {endGAD - startGAD} seconds")


# start2 = time.perf_counter()
# print(g.find("NESSES"))
# end2 = time.perf_counter()
# print(f"found in {end2 - start2} seconds")

r = ['B', 'O', 'S', 'O', 'T', 'Y', 'A']
row = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
anchor = 6
words = []


def gen(pos, word, rack, arc):
    if row[anchor + pos]:
        letter = row[anchor + pos]
        if arc.destination.arc_exists(letter):
            go_on(pos, letter, word, rack, arc.destination.outgoing_arcs[letter])
    elif len(rack) > 0:
        for letter in rack:
            if letter in arc.final_letters:
                if pos <= 0:
                    words.append(letter + word)
                else:
                    words.append(word + letter)
            if arc.destination.arc_exists(letter):
                c = rack.copy()
                c.remove(letter)
                go_on(pos, letter, word, c, arc.destination.outgoing_arcs[letter])
    elif Path.DELIMITER in arc.final_letters:
        words.append(word)

def go_on(pos, L, word, rack, new_arc):
    if pos <= 0:
        new_word = L + word
        if anchor - pos > 0 and not row[anchor + pos - 1]:
            gen(pos - 1, new_word, rack, new_arc)
        if (anchor - pos == 0 or not row[anchor - pos - 1]) and anchor < 14 and not row[anchor + 1] and new_arc.destination.arc_exists(Path.DELIMITER):
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


