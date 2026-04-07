import os
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form, BackgroundTasks

from app.db.mongo import db
from app.auth.dependencies import get_current_user

from app.upload.service import extract_pdf_structure, process_document_pipeline
from app.upload.structure import detect_structure
from app.upload.chunker import create_chunks
from app.vectordb.service import index_file_chunks

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/file")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    doc_type: str = Form(...),  # legal | financial | documentation
    current_user: str = Depends(get_current_user)
):
    
    print(f"[upload.routes.upload_file] file: {file}")
    print(f"[upload.routes.upload_file] doc_type: {doc_type}")
    print(f"[upload.routes.upload_file] current_user: {current_user}")

    # Validate file
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    # Validate doc_type
    if doc_type not in ["legal", "financial", "documentation"]:
        raise HTTPException(status_code=400, detail="Invalid document type")

    # Assign template automatically
    template_id = f"{doc_type}_v1"

    template = await db["templates"].find_one({"template_id": template_id})

    if not template:
        raise HTTPException(status_code=500, detail="Template not found")

    template_attributes = template["attributes"]

    # Enforce single processing per user
    existing_processing = await db["documents"].find_one({
        "uploaded_by": current_user,
        "$or": [ { "status": "processing" }, { "status": "indexing" } ]
    })

    if existing_processing:
        raise HTTPException(
            status_code=400,
            detail="You already have a document being processed"
        )

    # Save file
    file_id = str(uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Consistency flag (your requirement)
    requires_consistency = doc_type in ["legal", "financial"]

    # Store document
    doc = {
        "file_id": file_id,
        "filename": file.filename,
        "path": file_path,
        "doc_type": doc_type,
        "template_id": template_id,
        "uploaded_by": current_user,
        "status": "processing",  # immediately processing
        "requires_consistency": requires_consistency,
        "created_at": datetime.now(timezone.utc),
    }

    await db["documents"].insert_one(doc)
    
    print("[upload.routes.upload_file] Adding task to background")

    background_tasks.add_task(process_document_pipeline, file_id)

    indexed_count = await index_file_chunks(file_id)
    
    print("[upload.routes.upload_file] Indexed:", indexed_count)

    await db["documents"].update_one(
        {"file_id": file_id},
        {
            "$set": {
                "status": "completed",
                "indexed_chunks": indexed_count
            }
        }
    )

    return {
        "message": "File uploaded and processing started",
        "file_id": file_id,
        "template_used": template_id
    }