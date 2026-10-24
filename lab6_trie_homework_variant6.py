from __future__ import annotations

import sys

from trie import Trie

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


class Homework(Trie):

    def _ensure_str(self, value, name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"Illegal argument for {name}: expected str, got {type(value).__name__}"
            )
        return value

    def count_words_with_suffix(self, pattern) -> int:
        pattern = self._ensure_str(pattern, "count_words_with_suffix")
        if pattern == "":
            return self.size

        count = 0
        for word in self.keys():
            if word.endswith(pattern):
                count += 1
        return count

    def has_prefix(self, prefix) -> bool:
        prefix = self._ensure_str(prefix, "has_prefix")
        if prefix == "":
            return self.size > 0

        current = self.root
        for char in prefix:
            if char not in current.children:
                return False
            current = current.children[char]

        if current.value is not None:
            return True
        return len(current.children) > 0

    def shortest_word(self):
        words = self.keys()
        if not words:
            return None
        min_len = min(len(w) for w in words)
        candidates = [w for w in words if len(w) == min_len]
        return min(candidates)

    def count_words_ending_with(self, pattern) -> int:
        pattern = self._ensure_str(pattern, "count_words_ending_with")
        return self.count_words_with_suffix(pattern)


def run_tests() -> None:
    print("=" * 60)
    print("| Завдання 2 | Trie | Варіант 6")
    print("=" * 60)

    trie = Homework()
    words = ["apple", "application", "banana", "cat"]
    for i, word in enumerate(words):
        trie.put(word, i)

    print(f"Слова у дереві: {trie.keys()}")
    print()

    assert trie.count_words_with_suffix("e") == 1
    assert trie.count_words_with_suffix("ion") == 1
    assert trie.count_words_with_suffix("a") == 1
    assert trie.count_words_with_suffix("at") == 1
    print("count_words_with_suffix: OK")
    print(f"  suffix 'e'   → {trie.count_words_with_suffix('e')}")
    print(f"  suffix 'ion' → {trie.count_words_with_suffix('ion')}")
    print(f"  suffix 'a'   → {trie.count_words_with_suffix('a')}")
    print(f"  suffix 'at'  → {trie.count_words_with_suffix('at')}")

    assert trie.has_prefix("app") is True
    assert trie.has_prefix("bat") is False
    assert trie.has_prefix("ban") is True
    assert trie.has_prefix("ca") is True
    print("has_prefix: OK")
    print(f"  prefix 'app' → {trie.has_prefix('app')}")
    print(f"  prefix 'bat' → {trie.has_prefix('bat')}")
    print(f"  prefix 'ban' → {trie.has_prefix('ban')}")
    print(f"  prefix 'ca'  → {trie.has_prefix('ca')}")

    assert trie.shortest_word() == "cat"
    assert trie.count_words_ending_with("e") == 1
    assert trie.count_words_ending_with("ion") == 1
    assert trie.count_words_ending_with("xyz") == 0
    print("shortest_word / count_words_ending_with (варіант 6): OK")
    print(f"  shortest_word() → {trie.shortest_word()!r}")
    print(f"  ending_with 'e' → {trie.count_words_ending_with('e')}")
    print(f"  ending_with 'xyz' → {trie.count_words_ending_with('xyz')}")

    try:
        trie.has_prefix(123)  # type: ignore
        raise AssertionError("очікували TypeError")
    except TypeError:
        print("TypeError для некоректного has_prefix: OK")

    try:
        trie.count_words_with_suffix(None)  # type: ignore
        raise AssertionError("очікували TypeError")
    except TypeError:
        print("TypeError для некоректного count_words_with_suffix: OK")

    print()
    print("Усі тести пройшли успішно!")


if __name__ == "__main__":
    run_tests()
