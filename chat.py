import requests
import json # 解析模型返回的 json 数据

API_URL = "http://localhost:8080/v1/chat/completions"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "test-key"
}

# 流式聊天
def chat(messages):
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "temperature": 0.7,
        "stream": True #开启流式回复
    }

    try:
        with requests.post(API_URL, headers=HEADERS, json=payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines(decode_unicode=True): #流式需要逐行读取数据
                if not line or line.startswith(":"): #跳过空行和以 “:”开头的行（不是模型生成的内容）
                    continue
                if line.strip() == "data: [DONE]": # 结束
                    break
                if line.startswith("data:"): # 所需数据
                    data = line[len("data:"):].strip() # 去掉前缀
                    try:
                        chunk = json.loads(data) # 解析 json 
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "") # 回复内容
                        if content:
                            yield content # 流式返回
                    except json.JSONDecodeError as e:
                        print("[ERROR] JSON解析失败:", e)
                        continue
    except Exception as e:
        print("Error (stream) calling model:", e)
        yield "对不起，模型流式回复出错了。"


