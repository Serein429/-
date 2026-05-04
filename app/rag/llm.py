'''
from dotenv import load_dotenv
import os
import requests

load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def ask_llm(context, query):
    url = "https://api.deepseek.com/v1/chat/completions"
    
    # 根据 context 是否为空，使用不同的 prompt
    if not context or context.strip() == "":
        # 无参考资料：让模型用自己的知识回答
        system_prompt = "你是一个乐于助人的智能助手。请用你自身的知识回答用户的问题。"
        user_prompt = f"用户问题：{query}\n\n请直接回答，不需要参考任何外部资料。"
    else:
        # 有参考资料：要求基于资料总结
        system_prompt = "你是一个善于总结和归纳的智能助手。你会基于提供的参考资料，用自己的话重构信息，而不是逐字抄写。"
        user_prompt = f"""
【参考资料】
{context}

【用户问题】
{query}

**严格遵守以下规则（违反将导致系统错误）：**
- 你的回答必须以“是的”或直接陈述事实开头，**绝对禁止**出现“根据”、“参考”、“依据”、“资料显示”等任何指向外部来源的词语。
- 直接给出结论，不要附加任何元评论（如“根据资料”）。
- 回答示例正确开头：“拉斯柯尼科夫最终向索尼娅坦白...”
- 回答错误开头（禁止）：“根据参考资料，拉斯柯尼科夫...”

请直接输出你的答案，不要解释你遵守了什么规则。

请基于以上参考资料回答问题。要求：
1. 总结、归纳并用你自己的话回答。
2. **不要在回答中提及“根据资料”、“参考资料”、“上下文”等任何字样**，直接给出答案内容。
3. 如果资料不足，直接说“根据现有资料无法提供准确总结”。
4. 不要重复资料中的原句，要提炼关键点。
"""
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.5,
        "top_p": 0.9
    }
    
    res = requests.post(url, headers=headers, json=data)
    return res.json()["choices"][0]["message"]["content"]
'''





from dotenv import load_dotenv
import os
import requests

load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def ask_llm(context, query):
    url = "https://api.deepseek.com/v1/chat/completions"
    
    # 根据 context 是否为空，使用不同的 prompt
    if not context or context.strip() == "":
        # 无参考资料：让模型用自己的知识回答（开启思考模式）
        system_prompt = "你是一位知识渊博、善于思考的智能助手。你会用你的常识和逻辑推理能力，给出有深度、有见地的回答。"
        user_prompt = f"用户问题：{query}\n\n请仔细思考并直接回答。可以进行分析、举例、对比，让你的回答富有洞察力。"
    else:
        # 有参考资料：要求进行深层次思考，而不仅仅是总结
        system_prompt = """你是一位善于思考的智能助手。你会基于用户提供的资料，结合你自己的知识储备和推理能力，进行分析、归纳、比较、推测，并给出有洞察的答案。你的回答应该像一位专家在分享见解，而不是机械地复述或总结资料。"""
        
        user_prompt = f"""
【参考资料】
{context}

【用户问题】
{query}

**请基于参考资料，并进行你自己的思考后回答。要求：**

1. **首先理解资料**：提取关键事实和逻辑关系。
2. **在此基础上进行深入分析**：可以包括：
   - 分析原因或动机
   - 比较不同观点或人物
   - 推测可能的结果或影响
   - 举出相关的例子
   - 指出资料中的潜在矛盾或不足（如有）
   - 结合你自己的知识进行合理补充（如果资料不足，可适当补充，但要说明“基于我的知识”）
3. **回答要流畅、自然、有深度**，避免“根据资料”、“参考资料显示”等前缀。
4. **如果资料严重不足，无法进行任何有意义的分析**，请直接说“资料不足，无法给出分析性回答”。

请直接输出你的回答（不要输出思考过程或规则说明）：
"""
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,   # 提高温度以允许更多创造性思考
        "top_p": 0.9
    }
    
    res = requests.post(url, headers=headers, json=data)
    answer = res.json()["choices"][0]["message"]["content"]
    
    # 可选：去除可能残留的“根据资料”等前缀（增强鲁棒性）
    import re
    answer = re.sub(r'^(根据|参考|依据)[^，,]*[,，]?\s*', '', answer)
    
    return answer



import httpx  # 需要安装：pip install httpx
import json

async def ask_llm_stream(context: str, query: str):
    url = "https://api.deepseek.com/v1/chat/completions"
    
    if not context or context.strip() == "":
        system_prompt = "你是一位知识渊博、善于思考的智能助手。"
        user_prompt = f"用户问题：{query}\n\n请仔细思考并直接回答。"
    else:
        system_prompt = "你是一位善于思考的智能助手，基于资料结合自身知识进行分析。"
        user_prompt = f"""
【参考资料】
{context}

【用户问题】
{query}

请基于参考资料，并进行你自己的思考后回答。要求：分析原因、对比观点、举例等。避免“根据资料”等前缀。
"""
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "top_p": 0.9,
        "stream": True
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", url, headers=headers, json=data) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk_json = json.loads(data_str)
                        delta = chunk_json["choices"][0]["delta"]
                        if "content" in delta:
                            yield delta["content"]
                    except:
                        continue