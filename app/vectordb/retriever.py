from app.vectordb.chroma_client import collection


def retrieve_chunks(query: str, k: int = 5):
    # BGE requires prefix
    query = "Represent this sentence for retrieval: " + query

    results = collection.query(
        query_texts=[query],
        n_results=k
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    chunks = []

    for doc, meta in zip(documents, metadatas):
        chunks.append({
            "text": doc,
            "metadata": meta
        })

    return chunks
