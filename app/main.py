'''
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os

from app.rag.pipeline import rag_pipeline

app = FastAPI()

# 挂载静态文件夹（用于网页）
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class Query(BaseModel):
    question: str
    category: Optional[str] = None

@app.post("/ask")
def ask(q: Query):
    result = rag_pipeline(q.question, q.category)
    return result

@app.get("/")
def index():
    return FileResponse("static/index.html")

'''




from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
import os
import asyncio

# 原有 RAG pipeline（非流式版本）
from app.rag.pipeline import rag_pipeline
# 流式 RAG pipeline（新增，需要创建）
from app.rag.pipeline import rag_pipeline_stream

app = FastAPI()

# 挂载静态文件夹（用于网页）
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class Query(BaseModel):
    question: str
    category: Optional[str] = None

# 保留原有接口（返回 JSON）
@app.post("/ask")
def ask(q: Query):
    result = rag_pipeline(q.question, q.category)
    return result

# 新增流式接口（返回纯文本流）
@app.post("/ask/stream")
async def ask_stream(q: Query):
    async def generate():
        async for chunk in rag_pipeline_stream(q.question, q.category):
            yield chunk
    return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")

@app.get("/")
def index():
    return FileResponse("static/index.html")