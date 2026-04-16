from __future__ import annotations

import pickle
from pathlib import Path


class DictionaryLoadError(Exception):
    pass


class Dictionary:
    def contains(self, word: str) -> bool:
        raise NotImplementedError

    def __contains__(self, word: str) -> bool:
        return self.contains(word)


class PickleDictionary(Dictionary):
    def __init__(self, words: set[str]) -> None:
        if not isinstance(words, set):
            raise ValueError("PickleDictionary expects a set of strings.")

        self._words: set[str] = {
            self._normalize(word)
            for word in words
            if isinstance(word, str) and word.strip()
        }

    @classmethod
    def from_pickle(cls, path: str | Path) -> "PickleDictionary":
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Dictionary file not found: {path}")

        try:
            with path.open("rb") as f:
                data = pickle.load(f)
        except Exception as exc:
            raise DictionaryLoadError(
                f"Failed to load dictionary from {path}"
            ) from exc

        if not isinstance(data, set):
            raise DictionaryLoadError(
                f"Expected pickle to contain a set[str], got {type(data).__name__}"
            )

        if not all(isinstance(word, str) for word in data):
            raise DictionaryLoadError("Dictionary contains non-string entries.")

        return cls(data)

    @staticmethod
    def _normalize(word: str) -> str:
        return word.strip().upper()

    def contains(self, word: str) -> bool:
        return self._normalize(word) in self._words

    def __len__(self) -> int:
        return len(self._words)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(size={len(self._words)})"