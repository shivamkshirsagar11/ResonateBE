from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

client = AsyncIOMotorClient(MONGO_URI)

db = client["resonate_db"]

async def get_db():
    return db

async def create_indexes():
    await db.users.create_index("username", unique=True)
    await db.users.create_index("email", unique=True)
