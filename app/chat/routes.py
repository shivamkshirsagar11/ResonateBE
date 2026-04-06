from fastapi import APIRouter, Depends, Query
from typing import Optional

from app.db.mongo import db
from app.auth.dependencies import get_current_user
from app.core.utils import serialize_mongo_list

router = APIRouter()


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