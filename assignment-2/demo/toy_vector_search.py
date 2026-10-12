"""Toy demo of what a vector database does: embed text, search by similarity, filter metadata.

Real systems use a neural embedding model; here a simple bag-of-words vector is used
so the demo runs with only numpy and no downloads or API keys.
"""
import numpy as np

DOCS = [
    {'text': 'How to reset your account password',          'dept': 'IT'},
    {'text': 'Steps for account recovery if you forgot the password', 'dept': 'IT'},
    {'text': 'Annual leave policy and how to apply for vacation',   'dept': 'HR'},
    {'text': 'Maternity and paternity leave rules',                  'dept': 'HR'},
    {'text': 'Reimbursement process for travel expenses',            'dept': 'Finance'},
]

STOP = {'to', 'for', 'and', 'the', 'how', 'if', 'you', 'your', 'of', 'a'}
tokens = lambda t: [w for w in t.lower().split() if w not in STOP]
VOCAB = sorted({w for d in DOCS for w in tokens(d['text'])})


def embed(text):
    """Turn text into a vector of word counts (stand-in for a neural embedding)."""
    words = tokens(text)
    return np.array([words.count(w) for w in VOCAB], dtype=float)


def cosine(a, b):
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(a @ b / denom) if denom else 0.0


INDEX = [(embed(d['text']), d) for d in DOCS]      # the "vector database"


def search(query, top_k=2, dept=None):
    q = embed(query)
    hits = [(cosine(q, v), d) for v, d in INDEX if dept is None or d['dept'] == dept]
    return sorted(hits, key=lambda h: h[0], reverse=True)[:top_k]


if __name__ == '__main__':
    for query, dept in [('forgot password recovery', None),
                        ('leave policy', 'HR'),
                        ('leave policy', 'Finance')]:
        print(f'\nQuery: "{query}"  (filter: {dept})')
        for score, d in search(query, dept=dept):
            print(f'  {score:.2f}  [{d["dept"]}] {d["text"]}')
