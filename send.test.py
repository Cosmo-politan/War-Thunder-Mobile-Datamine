import requests

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1358669581388087470/Q3JgZ7kM-0tDQn4UOU7h9UC8y2Sb_lXNBujY8OjHz1tN04_zXwPDR1pB0VE3PjXL-IE0"
data = {
    "content": "테스트 메시지입니다."
}

response = requests.post(DISCORD_WEBHOOK, json=data)
print("Status Code:", response.status_code)
print("Response:", response.text)
