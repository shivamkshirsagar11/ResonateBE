from fastapi import APIRouter, Depends, Query
from typing import Optional
from pydantic import BaseModel

from app.db.mongo import db
from app.auth.dependencies import get_current_user
from app.core.utils import serialize_mongo_list
from app.vectordb.retriever import retrieve_chunks
from app.chat.service import build_context, generate_answer, rerank_chunks

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

@router.get("/debug/chunks")
async def get_chunks(
    file_id: str,
    limit: int = Query(10, le=50),
    section: Optional[str] = None,  # 🔥 NEW
    current_user: str = Depends(get_current_user)
):
    query = {"file_id": file_id}

    # 🔥 Optional filter
    if section:
        query["metadata.section"] = query["metadata.section"] = {"$regex": section, "$options": "i"}

    chunks = await db["chunks"].find(query)\
        .sort("order", 1)\
        .limit(limit)\
        .to_list(limit)

    chunks = serialize_mongo_list(chunks)

    return {"chunks": chunks}

@router.post("/query")
async def query_docs(
    request: QueryRequest,
    current_user: str = Depends(get_current_user)
):
    # retrieve
    chunks = retrieve_chunks(request.question, k = 20)
    chunks = rerank_chunks(request.question, chunks)

    # build context
    context = build_context(chunks)

    # generate answer
    answer = generate_answer(request.question, context)

    return {
        "answer": answer,
        "sources": chunks
    }
