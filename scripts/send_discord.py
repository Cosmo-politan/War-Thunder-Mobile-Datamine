import requests

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1358669581388087470/Q3JgZ7kM-0tDQn4UOU7h9UC8y2Sb_lXNBujY8OjHz1tN04_zXwPDR1pB0VE3PjXL-IE0"


MAX_LENGTH = 1900

def send_to_discord(text):
    print("[*] Sending changelog to Discord...")

    
    chunks = [text[i:i+MAX_LENGTH] for i in range(0, len(text), MAX_LENGTH)]

    for i, chunk in enumerate(chunks):
        content = f"**[자동 Changelog - {i+1}/{len(chunks)}]**\n```diff\n{chunk}\n```"
        response = requests.post(DISCORD_WEBHOOK, json={"content": content})
        if response.status_code in (200, 204):
            print(f"[+] Chunk {i+1} sent successfully.")
        else:
            print(f"[!] Failed to send chunk {i+1}: {response.status_code} - {response.text}")

if __name__ == "__main__":
    with open("changelog.txt", "r", encoding="utf-8") as f:
        changelog = f.read()
    send_to_discord(changelog)
