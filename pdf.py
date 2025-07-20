import requests
import json

API_URL = "http://localhost:8080/v1/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "test-key"
}

# 文字补全（流式）
def generate_text(prompt):
    payload = {
        "model": "gpt-3.5-turbo",
        "prompt": prompt,
        "temperature": 0,
        "stream": True
    }

    try:
        with requests.post(API_URL, headers=HEADERS, json=payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines(decode_unicode=True):
                if not line or line.startswith(":"):
                    continue
                if line.strip() == "data: [DONE]":
                    break
                if line.startswith("data:"):
                    data = line[len("data:"):].strip()
                    try:
                        chunk = json.loads(data)
                        content = chunk["choices"][0].get("text", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        yield f"Error generating text: {str(e)}"

# 文件总结
def generate_summary(current_file_text: str):
    summary_prompt = f"Please strictly output the following content:\n\n{current_file_text}"
    return summary_prompt

# 问题生成
def generate_question(current_file_text: str, content: str):
    question = f"Please answer the question: '{content}' based on the following content:\n\n{current_file_text}"
    return question