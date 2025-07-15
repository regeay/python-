import requests

def chat(messages):
    url = "http://localhost:8080/v1/chat/completions"

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "temperature": 0.7
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "test-key"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Error calling model:", e)
        return "对不起，模型回复出错了。"

