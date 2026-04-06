def serialize_mongo_document(doc):
    if not doc:
        return doc

    doc["_id"] = str(doc["_id"])
    return doc


def serialize_mongo_list(docs):
    return [serialize_mongo_document(doc) for doc in docs]
