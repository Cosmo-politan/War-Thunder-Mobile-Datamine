import os
import requests
import zipfile
from datetime import datetime
from utils.unpacker import unpack_apk
from utils.changelog import generate_changelog
from utils.discord import send_text_chunks_to_discord, send_images_to_discord

APK_URL = "https://wtmobile.com/apk"
WEBHOOK_URL = "https://discord.com/api/webhooks/1358669581388087470/Q3JgZ7kM-0tDQn4UOU7h9UC8y2Sb_lXNBujY8OjHz1tN04_zXwPDR1pB0VE3PjXL-IE0"

def download_apk():
    print("[*] APK 다운로드 중...")
    apk_path = "latest.apk"
    r = requests.get(APK_URL)
    with open(apk_path, "wb") as f:
        f.write(r.content)
    print("[+] APK 다운로드 완료")
    return apk_path

def run_pipeline():
    version = datetime.now().strftime("%Y%m%d")
    unpack_dir = f"unpacked/{version}"
    os.makedirs(unpack_dir, exist_ok=True)

    apk_path = download_apk()
    unpack_apk(apk_path, unpack_dir)

    if os.path.exists("previous_version"):
        changelog, changed_images = generate_changelog("previous_version", unpack_dir)
        if changelog:
            send_text_chunks_to_discord(changelog, WEBHOOK_URL, version)
            if changed_images:
                send_images_to_discord(changed_images, WEBHOOK_URL, version)
    else:
        print("[!] 최초 실행으로 이전 버전 없음.")

    os.system(f"rm -rf previous_version && cp -r {unpack_dir} previous_version")

if __name__ == "__main__":
    run_pipeline()
