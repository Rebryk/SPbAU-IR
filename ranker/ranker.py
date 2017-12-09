from data import Document
from collections import namedtuple


AbstractAndArticle = namedtuple("AbstractAndArticle", ["article", "abstract"])


class Ranker:
    def __init__(self):
        pass

    def rank(self, query: str, top_count: int) -> [AbstractAndArticle]:
        pass