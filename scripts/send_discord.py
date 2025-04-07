import requests

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1358669581388087470/Q3JgZ7kM-0tDQn4UOU7h9UC8y2Sb_lXNBujY8OjHz1tN04_zXwPDR1pB0VE3PjXL-IE0"
MAX_LENGTH = 1900

def send_to_discord(text):
    print("[*] Sending changelog to Discord...")

    if not text.strip():
        print("[*] No changes to send.")
        return

    parts = [text[i:i + MAX_LENGTH] for i in range(0, len(text), MAX_LENGTH)]

    for idx, part in enumerate(parts):
        try:
            data = {
                "content": f"**[자동 Changelog - Part {idx + 1}/{len(parts)}]**\n```\n{part}\n```"
            }
            print(f"[*] Sending part {idx+1}/{len(parts)}...")
            response = requests.post(DISCORD_WEBHOOK, json=data)

            print(f"[+] Response Code: {response.status_code}")
            print(f"[+] Response Text: {response.text}")

            if response.status_code not in [200, 204]:
                print(f"[!] Failed to send part {idx+1}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[!] Exception occurred while sending to Discord: {e}")

if __name__ == "__main__":
    try:
        with open("changelog.txt", "r", encoding="utf-8") as f:
            changelog = f.read().strip()

        if not changelog:
            print("[*] changelog.txt is empty. No message to send.")
        else:
            send_to_discord(changelog)
    except FileNotFoundError:
        print("[!] changelog.txt not found.")
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
