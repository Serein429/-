import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

COLLECTION_NAME = "papers_v1"  # ✅ 版本控制

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)