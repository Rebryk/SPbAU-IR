from nltk.stem.snowball import EnglishStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

class TextProcessor:
    def __init__(self):
        self._stemmer = EnglishStemmer()

    def process(self, text: str) -> [str]:
        words = filter(lambda word: word not in stopwords.words("english") and word.isalpha(), word_tokenize(text))
        return [self._stemmer.stem(word) for word in words]
