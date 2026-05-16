import pickle
from gaddag.GADDAG import GADDAG

def create_gaddag(d, out):
    nwl2023 = pickle.load(open(d, "rb"))

    g = GADDAG(nwl2023)
    pickle.dump(g, open(out, "wb"))

dictionary = "NWL2023.pickle"
output = "gaddagNWL2023-2.pickle"

create_gaddag(dictionary, output)