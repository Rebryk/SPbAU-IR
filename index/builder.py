from functools import reduce
from multiprocessing import Pool, cpu_count

from .index import Index


class IndexBuilder:
    def __init__(self, processes: int = cpu_count()):
        self._processes = processes
        self._pool = Pool(processes=self._processes)

    def build(self, index: Index, ids: [int]):
        indices = self._pool.map(index.build, self._partition(ids))
        return index(reduce(index.merge, indices, dict()))

    def _partition(self, ids: [int]):
        """ Group documents by hash"""

        for i in range(self._processes):
            yield [id for id in ids if id % self._processes == i]
