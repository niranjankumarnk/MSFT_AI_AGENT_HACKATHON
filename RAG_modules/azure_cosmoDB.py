import os
from dotenv import load_dotenv
import base64
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


load_dotenv()
MONGODB_URI = os.environ['MONGODB_URI2'] # Azure Cosmos DB connection string


# Create a new client and connect to the server
client = MongoClient(MONGODB_URI)


db = client["equipment_manuals"]

def store_manual_data(manual_name, chunks, embeddings, timestamp):
    collection = db[manual_name]
    collection.drop()  # remove duplicates

    for i, chunk in enumerate(chunks):
        doc = {
            "manual": manual_name,
            "timestamp": timestamp,
            "page": chunk.get("metadata", {}).get("page"),
            "text": chunk["text"],
            "embedding": embeddings[i],
            "image_urls": chunk.get("metadata", {}).get("image_urls", [])
        }
        collection.insert_one(doc)


def retrieve_manual_chunks(manual_name):
    collection = db[manual_name]
    return list(collection.find({}))

def list_manual_collections():
    return [name for name in db.list_collection_names() if not name.startswith("fs.")]


def delete_manual_data(manual_name):
    """
    Delete manual documents from MongoDB collection.
    """
    if manual_name in db.list_collection_names():
        db.drop_collection(manual_name)
        print(f"✅ Deleted manual collection: {manual_name}")
    else:
        print(f"⚠️ Manual {manual_name} not found in database.")

    

