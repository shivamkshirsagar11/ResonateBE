from app.vectordb.chroma_client import collection
from app.db.mongo import db
import asyncio

async def index_file_chunks(file_id: str):
    chunks = await db["chunks"].find({"file_id": file_id}).to_list(None)

    if not chunks:
        return 0

    print(f"Indexing file: {file_id}")
    print(f"Chunks fetched: {len(chunks)}")

    # 🔥 STEP 2: DELETE OLD VECTORS (CRITICAL)
    try:
        collection.delete(where={"file_id": file_id})
    except Exception as e:
        print(f"Delete warning: {e}")

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        ids.append(chunk["chunk_id"])
        documents.append(chunk["text"])

        metadata = chunk["metadata"].copy()

        # CRITICAL: MUST exist for delete to work
        metadata["file_id"] = file_id
        metadata["order"] = chunk["order"]

        metadatas.append(metadata)

    # 🔥 DEBUG CHECK (VERY IMPORTANT)
    print(f"Total IDs: {len(ids)}")
    print(f"Unique IDs: {len(set(ids))}")

    if len(ids) != len(set(ids)):
        print("❌ DUPLICATE IDS DETECTED IN BATCH")
        raise Exception("Duplicate chunk_ids in Mongo")

    
    BATCH_SIZE = 500

    for i in range(0, len(ids), BATCH_SIZE):
        batch_ids = ids[i:i+BATCH_SIZE]
        batch_docs = documents[i:i+BATCH_SIZE]
        batch_meta = metadatas[i:i+BATCH_SIZE]

        print(f"Indexing batch {i} → {i + len(batch_ids)}")

        collection.add(
            ids=batch_ids,
            documents=batch_docs,
            metadatas=batch_meta
        )

    print("Indexing complete")

    return len(ids)