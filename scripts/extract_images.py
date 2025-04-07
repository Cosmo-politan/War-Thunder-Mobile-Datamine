import os import requests

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1358669581388087470/Q3JgZ7kM-0tDQn4UOU7h9UC8y2Sb_lXNBujY8OjHz1tN04_zXwPDR1pB0VE3PjXL-IE0" MAX_LENGTH = 1900

def send_text_to_discord(text): print("[] Sending changelog text to Discord...") if not text.strip(): print("[] No changelog text to send.") return

chunks = [text[i:i + MAX_LENGTH] for i in range(0, len(text), MAX_LENGTH)]
for idx, chunk in enumerate(chunks):
    data = {
        "content": f"**[자동 Changelog - Part {idx + 1}/{len(chunks)}]**\n```diff\n{chunk}\n```"
    }
    response = requests.post(DISCORD_WEBHOOK, json=data)
    print(f"[*] Sent part {idx + 1}: {response.status_code}")
    if response.status_code not in [200, 204]:
        print("[!] Failed to send part:", response.text)

def send_images_to_discord(image_paths): print("[*] Sending images to Discord...") for image_path in image_paths: if not os.path.exists(image_path): print(f"[!] Image not found: {image_path}") continue

with open(image_path, 'rb') as f:
        files = {"file": (os.path.basename(image_path), f)}
        response = requests.post(DISCORD_WEBHOOK, files=files)

    print(f"[*] Sent image {image_path}: {response.status_code}")
    if response.status_code not in [200, 204]:
        print("[!] Failed to send image:", response.text)

if name == "main": # 1. 텍스트 changelog 전송 if os.path.exists("changelog.txt"): with open("changelog.txt", "r", encoding="utf-8") as f: changelog = f.read() send_text_to_discord(changelog)

# 2. 이미지 파일 전송 (예: 변경된 PNG 등)
image_dir = "extracted_images"  # 예: 변경된 이미지를 저장한 디렉터리
image_files = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith(".png")]
send_images_to_discord(image_files)

