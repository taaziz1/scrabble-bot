from pathlib import Path

import pytest

from scrabble_game.dictionary import PickleDictionary


@pytest.mark.skipif(not Path("../NWL2023.pickle").exists(), reason="Real dictionary file not available")
def test_real_dictionary_loads():
    dictionary = PickleDictionary.from_pickle("../NWL2023.pickle")
    assert len(dictionary) > 100000
    assert dictionary.contains("CAT") is True
    assert dictionary.contains("ZZZZZZZZ") is False