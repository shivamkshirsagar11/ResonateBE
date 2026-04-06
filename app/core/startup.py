from datetime import datetime, timezone
from app.db.mongo import db


TEMPLATES = [
    {
        "template_id": "legal_v1",
        "doc_type": "legal",
        "version": 1,
        "attributes": {
            "headers": 0.9,
            "sub_headers": 0.8,
            "clauses": 1.0,
            "tables": 0.7,
            "paragraphs": 0.5,
            "lists": 0.6
        }
    },
    {
        "template_id": "financial_v1",
        "doc_type": "financial",
        "version": 1,
        "attributes": {
            "headers": 0.8,
            "sub_headers": 0.7,
            "clauses": 0.6,
            "tables": 1.0,
            "paragraphs": 0.5,
            "lists": 0.6
        }
    },
    {
        "template_id": "documentation_v1",
        "doc_type": "documentation",
        "version": 1,
        "attributes": {
            "headers": 1.0,
            "sub_headers": 0.9,
            "clauses": 0.3,
            "tables": 0.4,
            "paragraphs": 0.7,
            "lists": 0.8
        }
    }
]


async def initialize_templates():
    templates_collection = db["templates"]

    for template in TEMPLATES:
        existing = await templates_collection.find_one({
            "template_id": template["template_id"],
            "version": template["version"]
        })

        if not existing:
            template["created_at"] = datetime.now(timezone.utc)
            template["updated_at"] = datetime.now(timezone.utc)

            await templates_collection.insert_one(template)
