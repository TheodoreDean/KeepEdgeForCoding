from openai import OpenAI

# 初始化客户端，指向本地 Ollama 服务
client = OpenAI(
    base_url='http://192.168.8.72:11434/v1',
    api_key='ollama', # 这里的 key 可以随便填，Ollama 不验证
)

response = client.chat.completions.create(
  model="llama3.1:8b", # 确保这里填的是你本地有的模型名
  messages=[
    {"role": "system", "content": "你是一个乐于助人的AI助手。"},
    {"role": "user", "content": "介绍一下量子纠缠。"}
  ]
)

print(response.choices[0].message.content)
