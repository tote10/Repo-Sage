import math
import re
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter

def tokenize(text: str) -> List[str]:
    # Extract words, camelCase and snake_case tokens
    tokens = re.findall(r"[A-Za-z0-9_]+", text.lower())
    sub_tokens = []
    for token in tokens:
        sub_tokens.append(token)
        parts = token.split("_")
        if len(parts) > 1:
            sub_tokens.extend([p for p in parts if p])
    return sub_tokens

class BM25Index:
    """Okapi BM25 index for exact lexical and symbol matching over code chunks."""
    def __init__(self, chunks: List[Dict[str, Any]], k1: float = 1.5, b: float = 0.75):
        self.chunks = chunks
        self.k1 = k1
        self.b = b
        self.doc_len: List[int] = []
        self.doc_freq: Dict[str, int] = Counter()
        self.doc_terms: List[Counter] = []
        self.avg_doc_len: float = 0.0
        self.num_docs: int = len(chunks)
        self._build()

    def _build(self) -> None:
        total_len = 0
        for chunk in self.chunks:
            # Index chunk text plus function/class name with higher weight
            full_text = f"{chunk.get('name', '')} {chunk.get('name', '')} {chunk['text']}"
            tokens = tokenize(full_text)
            term_counts = Counter(tokens)
            self.doc_terms.append(term_counts)
            doc_l = len(tokens)
            self.doc_len.append(doc_l)
            total_len += doc_l
            for term in term_counts:
                self.doc_freq[term] += 1

        self.avg_doc_len = (total_len / self.num_docs) if self.num_docs > 0 else 0.0

    def score(self, query: str) -> List[Tuple[float, Dict[str, Any]]]:
        if self.num_docs == 0:
            return []
        query_terms = tokenize(query)
        if not query_terms:
            return []

        scores: List[float] = [0.0] * self.num_docs
        for term in query_terms:
            df = self.doc_freq.get(term, 0)
            if df == 0:
                continue
            # Standard BM25 IDF with smoothing
            idf = math.log(1.0 + (self.num_docs - df + 0.5) / (df + 0.5))
            for doc_idx, term_counts in enumerate(self.doc_terms):
                tf = term_counts.get(term, 0)
                if tf == 0:
                    continue
                doc_l = self.doc_len[doc_idx]
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_l / self.avg_doc_len))
                scores[doc_idx] += idf * (numerator / denominator)

        ranked = [(scores[i], self.chunks[i]) for i in range(self.num_docs) if scores[i] > 0]
        ranked.sort(key=lambda x: x[0], reverse=True)
        return ranked

def keyword_search(query: str, chunks: List[Dict[str, Any]], k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
    index = BM25Index(chunks)
    return index.score(query)[:k]

if __name__ == "__main__":
    from rag.chunk import chunk_repo
    sample_chunks = chunk_repo()
    results = keyword_search("hash_password", sample_chunks, k=3)
    for score, chunk in results:
        print(f"BM25 {score:.3f}: {chunk['file']}:{chunk['start_line']} ({chunk['name']})")
