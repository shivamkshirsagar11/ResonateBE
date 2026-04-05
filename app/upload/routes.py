from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def upload_root():
    return {"message": "Upload route working"}