import os
import chromadb
from chromadb.utils import embedding_functions

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CHROMADB_PATH = os.path.join(BASE_DIR, "chroma_database")

# ensure directory exists
os.makedirs(CHROMADB_PATH, exist_ok=True)

client = chromadb.PersistentClient(path=CHROMADB_PATH)

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-base-en-v1.5"
)

collection = client.get_or_create_collection(
    name="resonate_chunks",
    embedding_function=embedding_function
)

print(f"[vectordb.chroma_client] size of collection {collection.count()}")
