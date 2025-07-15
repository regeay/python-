import os
import requests

def search(content):
    api_key = os.getenv("SERPAPI_API_KEY")  # !!!!!!请确保设置了环境变量
    if not api_key:
        raise ValueError("SERPAPI_API_KEY not set.")

    url = "https://serpapi.com/search"
    params = {
        "engine": "bing",
        "q": content,
        "api_key": api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    # 尝试取第一条 organic_results
    try:
        snippet = data["organic_results"][0]["snippet"]
    except (KeyError, IndexError):
        snippet = "No relevant search results found."

    prompt = f"Please answer the question: '{content}' based on the following search result:\n\n{snippet}"
    return prompt

