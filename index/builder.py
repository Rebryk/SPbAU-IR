from collections import namedtuple
from functools import reduce
from multiprocessing import Pool, cpu_count

from .index import Index

Document = namedtuple("Document", ["id", "text"])


class IndexBuilder:
    def __init__(self, processes: int):
        self._processes = processes or cpu_count()
        self._pool = Pool(processes=self._processes)

    def build(self, index: Index, documents):
        indices = self._pool.map(index.build, self._partition(documents))
        return index(reduce(index.merge, indices, dict()))

    @staticmethod
    def _partition(documents):
        """ Group documents by hash"""
        # TODO: implement
        return [documents]
