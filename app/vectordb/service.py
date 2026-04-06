from app.vectordb.chroma_client import collection
from app.db.mongo import db


async def index_file_chunks(file_id: str):
    chunks = await db["chunks"].find({"file_id": file_id}).to_list(None)

    if not chunks:
        print("[vectordb.service.index_file_chunks] No chunks found, returning...")
        return 0

    # remove old entries
    collection.delete(where={"file_id": file_id})
    
    await db["documents"].update_one(
        {"file_id": file_id},
        {"$set": {"status": "indexing"}}
    )

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        ids.append(chunk["chunk_id"])
        documents.append(chunk["text"])

        metadata = chunk["metadata"].copy()
        metadata["file_id"] = file_id
        metadata["order"] = chunk["order"]

        metadatas.append(metadata)

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    
    print("[vectordb.service.index_file_chunks] Indexed:", len(ids))
    
    await db["documents"].update_one(
        {"file_id": file_id},
        {"$set": {"status": "indexing completed"}}
    )

    return len(ids)