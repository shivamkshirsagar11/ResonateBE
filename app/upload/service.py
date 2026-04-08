import pdfplumber
from app.db.mongo import db
from app.upload.structure import detect_structure, merge_lines_to_paragraphs, clean_toc_noise, is_noise_block
from app.upload.chunker import create_chunks
from app.vectordb.service import index_file_chunks

async def extract_pdf_structure(file_path: str):
    pages_data = []

    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):

            text = page.extract_text() or ""

            tables = page.extract_tables()

            pages_data.append({
                "page": page_number,
                "text": text,
                "tables": tables
            })

    return pages_data

async def process_document_pipeline(file_id: str):
    doc = await db["documents"].find_one({"file_id": file_id})

    file_path = doc["path"]
    template_id = doc["template_id"]
    requires_consistency = doc["requires_consistency"]

    await db["chunks"].delete_many({"file_id": file_id})

    # parsing
    pages_data = await extract_pdf_structure(file_path)

    # structure
    structured_blocks = detect_structure(pages_data)
    print("Structured blocks:", len(structured_blocks))

    # merged blocks
    merged_blocks = merge_lines_to_paragraphs(structured_blocks)
    print("After merge:", len(merged_blocks))
    
    if merged_blocks:
        print("\n===== SAMPLE MERGED BLOCK =====\n")
        print(merged_blocks[0]["text"][:500])

    # template
    template_doc = await db["templates"].find_one({
        "template_id": template_id
    })
    template = template_doc["attributes"]

    # chunking
    chunks = create_chunks(merged_blocks, template, requires_consistency)
    print("Chunks created:", len(chunks))
    for c in chunks[:2]:
        print("\n===== SAMPLE CHUNK =====\n")
        print(c["text"][:300])

    # store chunks
    chunk_docs = []
    for i, chunk in enumerate(chunks):
        chunk_docs.append({
            "chunk_id": f"{file_id}_{i}",
            "file_id": file_id,
            "text": chunk["text"],
            "metadata": chunk["metadata"],
            "token_count": chunk["token_count"],
            "order": chunk["order"]
        })

    if chunk_docs:
        await db["chunks"].insert_many(chunk_docs)

    # index to chroma
    indexed_count = await index_file_chunks(file_id)
    print("[upload.routes.upload_file] Indexed:", indexed_count)

    # mark complete
    await db["documents"].update_one(
        {"file_id": file_id},
        {
            "$set": {
                "status": "completed",
                "indexed_chunks": indexed_count
            }
        }
    )
