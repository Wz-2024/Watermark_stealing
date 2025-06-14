import openai
from openai import OpenAI, AuthenticationError, APIConnectionError, BadRequestError

# 初始化客户端
client = OpenAI(
    api_key="sk-cwc0kIxuSiezRF7lmQd3R5QBCARLOkR1N8ZtEyQ4h5HGKMjx"
)

try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": "你好，GPT-4o，你能正常工作吗？"}
        ]
    )

    print("✅ 成功调用 GPT-4o！返回内容如下：\n")
    print(response.choices[0].message.content)

except AuthenticationError:
    print("❌ API Key 无效，请检查你的密钥。")

except BadRequestError as e:
    print("⚠️ 请求无效（参数错误或格式错误）：", str(e))

except APIConnectionError:
    print("⚠️ 无法连接到 OpenAI（检查网络或代理设置）。")

except Exception as e:
    print("⚠️ 发生其他未知错误：", str(e))
