import os
import requests

def image_generate(content: str) -> str:
    api_url = os.getenv('STABLE_DIFFUSION_API_URL', 'http://localhost:8080/v1/images/generations')
    
    # 构造请求参数
    data = {
        "prompt": content,
        "size": "256x256",  # 按要求固定尺寸为256x256
        "model": "stablediffusion"
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        # 发送请求
        response = requests.post(api_url, json=data, headers=headers, timeout=60)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析响应获取图片URL
        result = response.json()
        if result.get("data") and len(result["data"]) > 0:
            return result["data"][0].get("url", "")
        
        return ""
        
    except Exception as e:
        print(f"图片生成失败: {str(e)}")
        return ""
    
if __name__ == "__main__":
    image_generate('A cute baby sea otter')