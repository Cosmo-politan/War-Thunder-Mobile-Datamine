import requests

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1358669581388087470/Q3JgZ7kM-0tDQn4UOU7h9UC8y2Sb_lXNBujY8OjHz1tN04_zXwPDR1pB0VE3PjXL-IE0"

def send_to_discord(text):
    print("[*] Sending changelog to Discord...")
    data = {"content": f"**[자동 Changelog]**\n```diff\n{text}\n```"}
    response = requests.post(DISCORD_WEBHOOK, json=data)
    if response.status_code == 204:
        print("[+] Sent to Discord successfully.")
    else:
        print("[!] Failed to send to Discord:", response.status_code)

if __name__ == "__main__":
    with open("changelog.txt", "r", encoding="utf-8") as f:
        changelog = f.read()
    send_to_discord(changelog)
