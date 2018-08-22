from .ranker import Ranker, AbstractAndArticle
from text_processing import TextProcessor
from index import InvertedIndex
from collections import Counter, namedtuple
import math
import os

VecAndNorm = namedtuple("VecAndNorm", ["vec", "norm"])


class TfIdf(Ranker):
    def __init__(self,
                 index: InvertedIndex,
                 text_processor: TextProcessor,
                 documents: [AbstractAndArticle],
                 vectors_per_file: int,
                 vectors_save_folder: str):
        super().__init__()
        self.index = index.index
        self.token_id = {}
        self.text_processor = text_processor
        self.document_count = len(documents)
        self.vectors_per_file = vectors_per_file
        for i, token in enumerate(self.index.keys()):
            self.token_id[token] = i
        self.vectors_save_folder = vectors_save_folder

        for i in range(0, len(documents), self.vectors_per_file):
            document_batch = documents[i: min(len(documents), i + self.vectors_per_file)]
            with open(os.path.join(self.vectors_save_folder, "part_{}".format(i)), "w") as dump_file:
                for doc in document_batch:
                    dump_file.write(str(doc.article.id) + " ")

                    vec, norm = self.get_vec(doc.abstract)
                    dump_file.write("{:6f} ".format(norm))

                    for idx, val in vec.items():
                        dump_file.write("{} {:6f} ".format(idx, val))

                    dump_file.write("\n")

        self.dump_files_count = (len(documents) + min(self.vectors_per_file, len(documents)) - 1) // len(documents)

    @staticmethod
    def _cos_dist(query_vec, query_norm, doc_vec, doc_norm):
        sum = 0
        for term in query_vec:
            sum += query_vec[term] * doc_vec.get(term, 0)
        return sum / query_norm / doc_norm

    def rank(self, query: str, top_count: int) -> [int]:
        query_vec, query_norm = self.get_vec(query, process=True)
        if query_norm == 0:
            return []

        scores_and_documents = []

        for i in range(0, self.dump_files_count):
            with open(os.path.join(self.vectors_save_folder, "part_{}".format(i)), "r") as dump_file:
                for line in dump_file.readlines():
                    tokens = line.strip().split()

                    article_id, doc_norm = int(tokens[0]), float(tokens[1])
                    doc_vec = {int(tokens[i]): float(tokens[i + 1]) for i in range(2, len(tokens), 2)}

                    dist = TfIdf._cos_dist(query_vec, query_norm, doc_vec, doc_norm)
                    if dist > 0:
                        scores_and_documents.append((dist, article_id))

        scores_and_documents.sort(reverse=True)
        return list(map(lambda x: x[1], scores_and_documents[:top_count]))

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
