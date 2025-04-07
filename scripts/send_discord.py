import requests

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1358669581388087470/Q3JgZ7kM-0tDQn4UOU7h9UC8y2Sb_lXNBujY8OjHz1tN04_zXwPDR1pB0VE3PjXL-IE0"  

MAX_LENGTH = 1900

def send_to_discord(text):
    print("[*] Sending changelog to Discord...")
    if not text.strip():
        print("[*] No changes to send.")
        return

    chunks = [text[i:i + MAX_LENGTH] for i in range(0, len(text), MAX_LENGTH)]
    for chunk in chunks:
        data = {"content": f"**[자동 Changelog]**\n```diff\n{chunk}\n```"}
        response = requests.post(DISCORD_WEBHOOK, json=data)
        if response.status_code in (200, 204):
            print("[+] Sent chunk to Discord.")
        else:
            print(f"[!] Failed to send chunk: {response.status_code}")
