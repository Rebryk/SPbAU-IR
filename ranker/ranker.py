from collections import namedtuple


AbstractAndArticle = namedtuple("AbstractAndArticle", ["article", "abstract"])


class Ranker:
    def __init__(self):
        pass

    # returns list of ids of articles
    def rank(self, query: str, top_count: int) -> [int]:
        pass