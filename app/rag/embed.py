from sentence_transformers import SentenceTransformer


# ✅ 多语言模型（1024维）
model_path = r"D:\models\bge-m3\BAAI\bge-m3"
model = SentenceTransformer(model_path)

def embed(texts):
    return model.encode(texts, normalize_embeddings=True).tolist()