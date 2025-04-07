print("[DEBUG] main.py에서 import 시도 중...")
# main.py 상단에 직접 붙여넣기
def unpack_apk(apk_path: str, output_dir: str):
    print("[DEBUG] unpack_apk 함수 호출됨!")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    subprocess.run(["7z", "x", apk_path, f"-o{output_dir}"], check=True)

import os
import requests
from datetime import datetime
from utils.unpacker import unpack_apk
from utils.changelog import generate_changelog
# Discord 관련 모듈은 필요 시 추가
# from utils.discord import send_text_chunks_to_discord, send_images_to_discord

APK_URL = "https://wtmobile.com/apk"
WEBHOOK_URL = "YOUR_WEBHOOK_URL"

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
            print("변경 로그:")
            print(changelog)
            # send_text_chunks_to_discord(changelog, WEBHOOK_URL, version)
            # send_images_to_discord(changed_images, WEBHOOK_URL, version)
        else:
            print("변경 사항 없음.")
    else:
        print("[!] 최초 실행으로 이전 버전 없음.")

    os.system(f"rm -rf previous_version && cp -r {unpack_dir} previous_version")

if __name__ == "__main__":
    run_pipeline()

import sys
print("현재 작업 디렉토리:", os.getcwd())
print("PYTHONPATH:", sys.path)
import sys
print("[DEBUG] sys.path:", sys.path)
