import glob
import gzip
import os
import pickle
from datetime import datetime


class Index:
    def __init__(self, name: str):
        self.name = name
        self.index = None

    def __call__(self, index: dict):
        self.index = index

    def save(self, folder: str):
        dump_name = datetime.now().strftime("{}_%Y_%m_%d_%H_%M_%S.pickle.gz".format(os.path.join(folder, self.name)))

        with gzip.open(dump_name, "wb") as dump:
            dump.write(pickle.dumps(self))

    @staticmethod
    def load(folder: str, name: str):
        dumps = glob.glob("{}*.pickle.gz".format(os.path.join(folder, name)))

        if not dumps:
            return None

        latest_dump_name = max(dumps)

        with gzip.open(latest_dump_name, "rb") as dump:
            return pickle.load(dump)

    @staticmethod
    def build(documents):
        """ Build index for the given documents """
        pass

    @staticmethod
    def merge(index_1: dict, index_2: dict):
        """ Merge two indices """
        pass
