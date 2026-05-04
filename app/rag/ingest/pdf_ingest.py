import os
import io
import fitz
import pytesseract
import hashlib
import re

from PIL import Image
from app.rag.embed import embed
from app.rag.vector_db import collection

fitz.TOOLS.mupdf_display_errors(False)

from paddleocr import PaddleOCR

ocr = PaddleOCR(
    use_angle_cls=True,
    lang="ch"# 支持中英混合
  
)


# ========= 工具函数 =========

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F\u4e00-\u9fffа-яА-Я.,!?;:()\- ]', '', text)
    return text.strip()


def detect_lang(text):
    if any('\u4e00' <= c <= '\u9fff' for c in text):
        return "[ZH]"
    elif any('а' <= c <= 'я' or 'А' <= c <= 'Я' for c in text):
        return "[RU]"
    return "[EN]"


def gen_id(file_path, i):
    file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
    return f"{file_hash}_{i}"


def ocr_image(image):
    try:
        import numpy as np

        img_np = np.array(image)

        result = ocr.predict(img_np)

        if not result or not result[0]:
            return ""

        texts = [word[1][0] for word in result[0] if len(word) >= 2]

        return "\n".join(texts)

    except Exception:
        return ""

# ========= PDF读取 =========

def read_pdf(path):
    text = ""

    try:
        doc = fitz.open(path)
    except:
        return ""

    for page in doc:
        page_text = ""

        try:
            page_text = page.get_text()
        except:
            pass

        # ✅ 永远保留文本（哪怕是垃圾）
        text += page_text

        # ✅ 同时做 OCR（关键！！！）
        try:
            images = page.get_images(full=True)

            for img in images:  # 控制数量
                try:
                    xref = img[0]
                    base = doc.extract_image(xref)
                    image = Image.open(io.BytesIO(base["image"])).convert("RGB")

                    ocr_text = ocr_image(image)

                    if len(ocr_text.strip()) > 10:
                        text += "\n" + ocr_text

                except:
                    pass
        except:
            pass

    return text


# ========= 切块 =========

def split_text(text, size=500, overlap=100):
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i + size])
        i += size - overlap
    return chunks


# ========= 递归读取 =========

def get_all_pdfs(data_dir):
    files = []
    for root, _, filenames in os.walk(data_dir):
        for f in filenames:
            if f.lower().endswith(".pdf"):
                full_path = os.path.join(root, f)
                category = os.path.basename(root)
                files.append((full_path, category))
    return files


# ========= 主入口 =========

def ingest(data_dir):

    pdf_files = get_all_pdfs(data_dir)

    for file_path, category in pdf_files:

        filename = os.path.basename(file_path)
        print(f"📄 处理: {filename}")

        text = read_pdf(file_path)

        if not text or len(text.strip()) < 10:
            print(f"⚠️ 跳过: {filename}")
            continue

        chunks = split_text(text)

        batch_size = 16

        for i in range(0, len(chunks), batch_size):

            batch_chunks = chunks[i:i + batch_size]

            batch_chunks = [clean_text(c) for c in batch_chunks]
            batch_chunks = [
                f"[{category}] " + detect_lang(c) + c
                for c in batch_chunks
            ]

            embs = embed(batch_chunks)

            collection.add(
                documents=batch_chunks,
                embeddings=embs,
                ids=[gen_id(file_path, i + j) for j in range(len(batch_chunks))],
                metadatas=[{
                    "category": category,
                    "filename": filename
                }] * len(batch_chunks)
            )

    print("🎉 导入完成")


if __name__ == "__main__":
    ingest(r"E:\大创项目\知识库")  # 👈 改成你的路径