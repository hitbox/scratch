import math
from collections import Counter

class BM25:
    def __init__(self, corpus, k1=1.5, b=0.75):
        self.corpus = corpus
        self.k1 = k1
        self.b = b
        self.avgdl = sum(len(doc) for doc in corpus) / len(corpus)
        self.df = self.compute_df()
        self.idf = self.compute_idf()

    def compute_df(self):
        df = Counter()
        for doc in self.corpus:
            terms = set(doc)
            df.update(terms)
        return df

    def compute_idf(self):
        idf = {}
        N = len(self.corpus)
        for term, freq in self.df.items():
            idf[term] = math.log((N - freq + 0.5) / (freq + 0.5) + 1)
        return idf

    def score(self, query):
        scores = Counter()
        for term in query:
            if term not in self.df:
                continue
            idf = self.idf[term]
            for doc in self.corpus:
                f = doc.count(term)
                dl = len(doc)
                score = idf * (f * (self.k1 + 1)) / (f + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
                scores[doc] += score
        return scores

    def sort(self, query):
        scores = self.score(query)
        return [doc for doc, score in scores.most_common()]

# Example usage:
corpus = [
    ["hello", "world"],
    ["hello", "python", "world"],
    ["python", "is", "awesome"],
    ["python", "is", "great"],
    ["programming", "is", "fun"]
]

bm25 = BM25(corpus)
query = ["python", "is"]
sorted_docs = bm25.sort(query)
print("Sorted documents based on BM25 scores:")
for doc in sorted_docs:
    print(doc)

# 2024-02-07 Wed.
# - reading this:
#   https://www.alexmolas.com/2024/02/05/a-search-engine-in-80-lines.html
# - https://chat.openai.com/c/83b9cb1e-8308-4f7f-a69b-92db88670dac
