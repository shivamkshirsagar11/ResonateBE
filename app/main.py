# Fastapi related
from fastapi import FastAPI

# from project libs
from app.db.mongo import create_indexes
from app.core.startup import initialize_templates

# Routers
from app.auth.routes import router as auth_router
from app.upload.routes import router as upload_router
from app.chat.routes import router as chat_router


app = FastAPI(title="Resonate BE 🚀")


# Startup event
@app.on_event("startup")
async def startup_event():
    await create_indexes()
    await initialize_templates()


# Root
@app.get("/")
def root():
    return {"message": "Resonate BE running 🚀"}


@app.get("/health")
def health():
    return {"status": "ok"}


# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(upload_router, prefix="/upload", tags=["Upload"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])