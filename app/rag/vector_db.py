import chromadb
import os

# 从环境变量读取连接信息
CHROMA_URL = os.getenv("CHROMA_URL")
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")

if not CHROMA_URL or not CHROMA_API_KEY:
    raise RuntimeError("Missing CHROMA_URL or CHROMA_API_KEY environment variables")

# 连接到远程 Railway Chroma（通过 Auth Proxy）
client = chromadb.HttpClient(
    host=CHROMA_URL,
    port=443,
    ssl=True,
    headers={"Authorization": f"Bearer {CHROMA_API_KEY}"},
    tenant="default_tenant",
    database="default_database"
)

COLLECTION_NAME = "papers_v1"
collection = client.get_or_create_collection(name=COLLECTION_NAME)
