import requests

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1358669581388087470/Q3JgZ7kM-0tDQn4UOU7h9UC8y2Sb_lXNBujY8OjHz1tN04_zXwPDR1pB0VE3PjXL-IE0"
MAX_LENGTH = 1900  # Discord 메시지 제한 고려 (2000자 - 여유)

def send_to_discord(text):
    print("[*] Sending changelog to Discord...")

    # 긴 메시지를 분할해서 전송
    parts = [text[i:i + MAX_LENGTH] for i in range(0, len(text), MAX_LENGTH)]

    for idx, part in enumerate(parts):
        data = {
            "content": f"**[자동 Changelog - Part {idx + 1}/{len(parts)}]**\n```diff\n{part}\n```"
        }
        response = requests.post(DISCORD_WEBHOOK, json=data)
        print(f"[*] Part {idx + 1}/{len(parts)} sent with status: {response.status_code}")
        if response.status_code not in [200, 204]:
            print("[!] Failed to send this part:", response.text)

if __name__ == "__main__":
    with open("changelog.txt", "r", encoding="utf-8") as f:
        changelog = f.read().strip()

    if not changelog:
        print("[*] No changes detected, nothing to send.")
    else:
        send_to_discord(changelog)
