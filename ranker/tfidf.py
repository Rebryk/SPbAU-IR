from .ranker import Ranker, AbstractAndArticle
from text_processing import TextProcessor
from data import Document
from index import InvertedIndex
from collections import Counter
import numpy as np


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
        query_vec = self.get_vec(query, process=True)

        def cos_dist(doc):
            doc_vec = doc[0]
            return np.sum(query_vec * doc_vec) / np.linalg.norm(query_vec) / np.linalg.norm(doc_vec)

        return list(map(lambda t: t[1], sorted(self.vec_and_document, key=cos_dist, reverse=True)[:top_count]))

    def get_vec(self, text: str, process=False) -> np.ndarray:
        if process:
            tokens = self.text_processor.process(text)
        else:
            tokens = text.split()
        doc_token_freq = Counter()
        for token in tokens:
            doc_token_freq[token] += 1

        vec = np.zeros(len(self.index), dtype=np.float32)
        for token in tokens:
            if token not in self.index:
                continue
            df = len(self.index[token])
            tf = doc_token_freq[token]
            idf = tf / np.log(self.document_count / df)
            token_id = self.token_id[token]
            vec[token_id] = idf
        return vec
