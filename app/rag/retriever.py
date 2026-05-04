from .embed import embed
from .vector_db import collection

'''
def search(query, top_k=5, category=None):

    query_emb = embed([query])[0]

    where = {}
    if category:
        where["category"] = category

    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k,
        where=where if where else None
    )

    return results["documents"][0]
'''
from .embed import embed
from .vector_db import collection

def search(query, top_k=5, category=None):

    query_emb = embed([query])[0]

    where = {}
    if category:
        where["category"] = category

    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k,
        where=where if where else None
    )

    docs = results["documents"][0]
    scores = results["distances"][0]

    # 返回 (文本, 分数)
    return list(zip(docs, scores))