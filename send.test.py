import requests

DISCORD_WEBHOOK = "https://discord.com/api/webhooks /1358669581388087470/Q3JgZ7kM

-0tDQn4U0U7h9UC8y2Sb

_lXNBujY80jHz1tN04

_zXwPDR1pB0VE3PjXL-IE0"
data = {
    "content": "**[테스트 메시지]**\n```diff\n+ 이것은 테스트입니다.\n- 실패 메시지를 확인하세요.\n```"
}

response = requests.post(DISCORD_WEBHOOK, json=data)
print("Status:", response.status_code)
print("Response:", response.text)
