from collections import namedtuple
from operator import attrgetter

from .index import Index

InvertedIndexEntry = namedtuple("InvertedIndexEntry", ["document", "count", "positions"])


class InvertedIndex(Index):
    NAME = "inverted_index"

    def __init__(self):
        super().__init__(InvertedIndex.NAME)

    @staticmethod
    def build(documents) -> dict:
        """ Build an index for the given documents """

        index = dict()

        for document in documents:
            for token in set(document.text):
                if token not in index:
                    index[token] = []

                index[token].append(InvertedIndex._build_entry(document, token))

        return index

    @staticmethod
    def merge(index1: dict, index2: dict):
        """ Merge two indices """

        return {token: InvertedIndex._merge(index1.get(token, []), index2.get(token, []))
                for token in index1.keys() | index2.keys()}

    @staticmethod
    def _merge(list1: [InvertedIndexEntry], list2: [InvertedIndexEntry]) -> [InvertedIndexEntry]:
        return sorted(list1 + list2, key=attrgetter("count"), reverse=True)

    @staticmethod
    def _gap_values(values: [int]):
        """ Compress list with ints """

        return [values[0]] + [values[i] - values[i - 1] for i in range(1, len(values))]

    @staticmethod
    def _build_entry(document, token: str) -> InvertedIndexEntry:
        """ Build an inverted index entry for the given text and token """

        positions = InvertedIndex._gap_values([index for index, word in enumerate(document.text) if word == token])
        return InvertedIndexEntry(document.id, len(positions), positions)
