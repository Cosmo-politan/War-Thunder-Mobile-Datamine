import requests, zipfile, os, subprocess

APK_URL = "https://wtmobile.com/apk"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1358669581388087470/Q3JgZ7kM-0tDQn4UOU7h9UC8y2Sb_lXNBujY8OjHz1tN04_zXwPDR1pB0VE3PjXL-IE0"

def download_apk():
    print("[*] Downloading latest APK...")
    r = requests.get(APK_URL)
    with open("wtmobile_latest.apk", "wb") as f:
        f.write(r.content)

def unpack_apk():
    print("[*] Unpacking APK...")
    os.makedirs("unpacked", exist_ok=True)
    subprocess.run(["unzip", "-o", "wtmobile_latest.apk", "-d", "unpacked"], check=True)

def send_discord_changelog(changelog):
    data = {"content": f"[자동 Changelog]
{changelog}"}
    requests.post(DISCORD_WEBHOOK, json=data)

def generate_changelog():
    # 간단한 changelog 예시
    return "- 신규 장비 발견
- 차량 성능 변경"

if __name__ == "__main__":
    download_apk()
    unpack_apk()
    changelog = generate_changelog()
    send_discord_changelog(changelog)

# 테스트용 주석입니다.
