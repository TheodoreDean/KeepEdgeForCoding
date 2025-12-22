# test for python connect to local AI

import requests
import json

url = "http://192.168.8.72:11434/api/generate"

data = {
    "model": "llama3.1:8b",
    "prompt": "用一句话解释什么是递归。",
    "stream": False # 设为 False 以便一次性获取结果，设为 True 需要处理流
}

response = requests.post(url, json=data)

if response.status_code == 200:
    result = response.json()
    print(result['response'])
else:
    print("Error:", response.status_code, response.text)
