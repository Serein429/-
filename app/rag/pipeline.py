'''
from .retriever import search
from .llm import ask_llm

def rag_pipeline(query, category=None, similarity_threshold=0.6):
    # 检索文档（假设 search 返回的是 (doc_text, score) 列表，需根据你的实现调整）
    results = search(query, category=category)   # 如果 search 只返回文本，你需要修改 retriever 返回分数
    
    # 如果没有检索结果，或者最高分低于阈值，直接让 LLM 用自身知识回答
    if not results:
        return {
            "answer": ask_llm("", query),   # 空 context
            "sources": []
        }
    
    # 如果你的 search 返回的只是字符串列表，无法获取分数，建议修改 retriever 返回 (text, score)
    # 临时方案：根据检索到的文本是否包含明显不相关关键词（如俄文、英文乱码）来过滤
    # 更规范的做法：修改 retriever.py 让 search 返回带分数的结果
    
    # 示例：假设你的 search 返回 [(text, score), ...]
    # relevant_docs = [text for text, score in results if score >= similarity_threshold]
    # if not relevant_docs:
    #     return {"answer": ask_llm("", query), "sources": []}
    
    # 临时简单方案：直接检查检索到的文本是否看起来像小说片段（包含"[原文]"等标记）
    # 注意：这不够优雅，建议还是修改检索器返回分数
    cleaned_docs = []
    for doc in results:
        if len(doc) < 20 or "[原文]" in doc or "EN]" in doc or "RU" in doc:
            continue   # 跳过明显是碎片或外文的资料
        cleaned_docs.append(doc)
    
    if not cleaned_docs:
        return {
            "answer": ask_llm("", query),
            "sources": []
        }
    
    context = "\n\n".join(cleaned_docs)
    answer = ask_llm(context, query)
    
    return {
        "answer": answer,
        "sources": cleaned_docs
    }

def rag_pipeline(query, category=None):
    # 问候类问题直接返回预设字符串
    greetings = ["你好", "自我介绍", "你是谁", "介绍一下你自己", "hello", "hi"]
    if any(g in query.lower() for g in greetings):
        # 直接返回你想要的回答，不调用 LLM
        custom_answer = "我是你的陀思妥耶夫斯基小助手，可以回答有关老陀的问题，请问有什么需要我帮你？"
        return {"answer": custom_answer, "sources": []}
    
    # 否则正常检索
    docs = search(query, category=category)
    context = "\n\n".join(docs)
    answer = ask_llm(context, query)
    return {"answer": answer, "sources": docs}
'''


from .retriever import search
from .embed import embed
from .llm import ask_llm
import numpy as np
import asyncio

SIMILARITY_THRESHOLD = 0.5

def rag_pipeline(query, category=None):
    # 问候语直接返回，不走 LLM（更快）
    greetings = ["你好", "hello", "hi", "你是谁", "介绍一下你自己", "what's your name", "你的名字"]
    if any(g in query.lower() for g in greetings):
        return "我是你的陀思妥耶夫斯基智能助手，可以进行文学分析与问题解答。"

    # 检索文档（注意：search 可能返回 [(doc_text, score), ...] 或 [doc_text, ...]）
    raw_docs = search(query, top_k=5, category=category)

    # 统一提取文本：如果是元组则取第一个元素，否则直接用
    docs = []
    for item in raw_docs:
        if isinstance(item, tuple):
            docs.append(item[0])
        else:
            docs.append(item)

    # 判断相关性
    relevant = False
    if docs:
        query_emb = embed([query])[0]
        doc_embs = embed(docs)
        sims = np.dot(doc_embs, query_emb)
        max_sim = np.max(sims)
        relevant = max_sim >= SIMILARITY_THRESHOLD

    if relevant:
        context = "\n\n".join(docs)
        answer = ask_llm(context, query)
    else:
        answer = ask_llm("", query)

    return answer   # 直接返回字符串，不包装成字典

# 原有的 rag_pipeline 保持不变，添加异步流式版本
async def rag_pipeline_stream(query: str, category: str = None):
    from .llm import ask_llm_stream
    from .retriever import search
    from .embed import embed
    import numpy as np

    # 问候类直接返回（也可以走流式，这里简单直接生成完整字符串）
    greetings = ["你好", "hello", "hi", "你是谁", "介绍一下你自己", "what's your name", "你的名字"]
    if any(g in query.lower() for g in greetings):
        yield "我是你的陀思妥耶夫斯基智能助手，可以进行文学分析与问题解答。"
        return

    # 检索并处理（注意：embed 和 search 是同步的，需要在线程池中运行以避免阻塞）
    # 如果 embed/search 很耗时，建议用 asyncio.to_thread 包装
    raw_docs = await asyncio.to_thread(search, query, top_k=5, category=category)
    docs = []
    for item in raw_docs:
        if isinstance(item, tuple):
            docs.append(item[0])
        else:
            docs.append(item)

    # 相关性判断
    relevant = False
    if docs:
        query_emb = await asyncio.to_thread(embed, [query])
        query_emb = query_emb[0]
        doc_embs = await asyncio.to_thread(embed, docs)
        sims = np.dot(doc_embs, query_emb)
        max_sim = np.max(sims)
        relevant = max_sim >= 0.5

    if relevant:
        context = "\n\n".join(docs)
        async for chunk in ask_llm_stream(context, query):
            yield chunk
    else:
        async for chunk in ask_llm_stream("", query):
            yield chunk