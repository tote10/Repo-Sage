from sentence_transformers import SentenceTransformer
from chunk import chunk_repo

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_chunks(chunks):
    vectors = model.encode([chunk["text"] for chunk in chunks])
    for c, v in zip(chunks, vectors):
        c["embedding"]= v
        return chunks
if __name__ == "__main__":
    chunks = embed_chunks(chunk_repo())
    print(f"{len(chunks)}chunks,vector length: {len(chunks[0]['embedding']) if chunks else 0}")