from send_discord import send_to_discord

if __name__ == "__main__":
    with open("changelog.txt", "r", encoding="utf-8") as f:
        changelog = f.read().strip()

    if not changelog:
        print("[*] No changes detected, nothing to send.")
    else:
        send_to_discord(changelog)
