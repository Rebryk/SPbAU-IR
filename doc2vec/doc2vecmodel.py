from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from data import Article
from sklearn.manifold import TSNE
import pickle


class Doc2VecModel:
    def __init__(self, vec_dim: int):
        self.vec_dim = vec_dim
        self.vecs2d = {}

    def fit(self, documents: [Article], epochs: int):
        train_docs = []
        for doc in documents:
            with open(doc.processed_abstract_path, 'r') as inp:
                words = inp.readline().strip().split(' ')
                train_docs.append(TaggedDocument(words, [doc.id]))

        model = Doc2Vec(size=self.vec_dim)
        model.build_vocab(train_docs)
        model.train(train_docs, epochs=epochs, total_examples=len(train_docs), compute_loss=True)

        vecs = {doc.id: model.docvecs[doc.id] for doc in documents}
        vecs2d = TSNE().fit_transform(list(vecs.values()))
        self.vecs2d = {key: vecs2d[i] for i, key in enumerate(vecs.keys())}

    def save_model(self, path: str):
        with open(path, "wb") as dump_file:
            pickle.dump(self, dump_file)

    @staticmethod
    def load_model(path: str):
        with open(path, "rb") as dump_file:
            return pickle.load(dump_file)

    def __getitem__(self, item: Article):
        return self.vecs2d[[item.id]]