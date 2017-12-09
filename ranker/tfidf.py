from .ranker import Ranker, AbstractAndArticle
from text_processing import TextProcessor
from index import InvertedIndex
from collections import Counter, namedtuple
import math

VecAndNorm = namedtuple("VecAndNorm", ["vec", "norm"])


class TfIdf(Ranker):
    def __init__(self, index: InvertedIndex, text_processor: TextProcessor, documents: [AbstractAndArticle]):
        super().__init__()
        self.index = index.index
        self.token_id = {}
        self.text_processor = text_processor
        self.document_count = len(documents)
        for i, token in enumerate(self.index.keys()):
            self.token_id[token] = i

        self.vec_and_document = [(self.get_vec(doc.abstract), doc) for doc in documents]

    def rank(self, query: str, top_count: int) -> [AbstractAndArticle]:
        query_vec, query_norm = self.get_vec(query, process=True)

        def cos_dist(doc):
            doc_vec, doc_norm = doc[0]
            sum = 0
            for term in query_vec:
                sum += query_vec[term] * doc_vec.get(term, 0)
            return sum / query_norm / doc_norm

        return list(map(lambda t: t[1], sorted(self.vec_and_document, key=cos_dist, reverse=True)[:top_count]))

    def get_vec(self, text: str, process=False) -> VecAndNorm:
        if process:
            tokens = self.text_processor.process(text)
        else:
            tokens = text.split()
        doc_token_freq = Counter()
        for token in tokens:
            doc_token_freq[token] += 1
        vec = {}
        sum = 0
        for token in tokens:
            if token not in self.index:
                continue
            df = len(self.index[token])
            tf = doc_token_freq[token]
            idf = tf / math.log(self.document_count / df)
            token_id = self.token_id[token]
            vec[token_id] = idf
            sum += idf ** 2
        return VecAndNorm(vec, math.sqrt(sum))
