import os
import requests

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1358669581388087470/Q3JgZ7kM-0tDQn4UOU7h9UC8y2Sb_lXNBujY8OjHz1tN04_zXwPDR1pB0VE3PjXL-IE0"
MAX_LENGTH = 190


def send_to_discord(text):
    print("[*] Sending changelog to Discord...")

    if not text.strip():
        print("[*] No changes to send.")
        return

    parts = [text[i:i + MAX_LENGTH] for i in range(0, len(text), MAX_LENGTH)]

    for idx, part in enumerate(parts):
        data = {
            "content": f"**[자동 Changelog - Part {idx + 1}/{len(parts)}]**\n```diff\n{part}\n```"
        }
        response = requests.post(DISCORD_WEBHOOK, json=data)
        if response.status_code in [200, 204]:
            print(f"[+] Part {idx + 1}/{len(parts)} sent.")
        else:
            print(f"[!] Failed to send part {idx + 1}: {response.status_code}")
            print("[!] Error:", response.text)


def send_images_to_discord(image_paths):
    print(f"[*] Sending {len(image_paths)} image(s) to Discord...")

    for img_path in image_paths:
        if not os.path.exists(img_path):
            print(f"[!] Skipping missing file: {img_path}")
            continue

        with open(img_path, "rb") as f:
            files = {"file": (os.path.basename(img_path), f)}
            data = {"content": f"변경된 이미지 파일: `{img_path}`"}
            response = requests.post(DISCORD_WEBHOOK, data=data, files=files)

        if response.status_code in [200, 204]:
            print(f"[+] Image sent: {img_path}")
        else:
            print(f"[!] Failed to send image {img_path}: {response.status_code}")
            print("[!] Error:", response.text)
