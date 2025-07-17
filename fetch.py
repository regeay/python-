import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

def fetch(url: str):

    try:
        # 发送HTTP请求
        response = requests.get(url)
        response.raise_for_status()

        # 解析HTML
        fetch_results = BeautifulSoup(response.text, 'html.parser')

        # 获取p标签的文本
        processed_results = fetch_results.select_one\
            ('body > main > div > section > div.border-r10 > p:nth-child(3)').get_text().strip()

        # 生成question
        question = f"Act as a summarizer. Please summarize {url}.\
              The following is the content:\n\n{processed_results}"
        return question
    
    except RequestException as e:
        return f"Failed to fetch {url}. Error: {str(e)}"
    except Exception as e:
        return f"An error occurred while processing {url}. Error: {str(e)}"
