import requests
import os

MAX_TEXT = 1900
MAX_IMAGES = 10

def send_text_chunks_to_discord(text, webhook, version):
    chunks = [text[i:i + MAX_TEXT] for i in range(0, len(text), MAX_TEXT)]
    for idx, chunk in enumerate(chunks):
        data = {
            "content": f"**[{version} Changelog - Part {idx+1}/{len(chunks)}]**\n```diff\n{chunk}\n```"
        }
        r = requests.post(webhook, json=data)
        print(f"[*] 텍스트 전송 상태: {r.status_code}")

def send_images_to_discord(images, webhook, version):
    for i in range(0, len(images), MAX_IMAGES):
        files = [('file', (os.path.basename(p), open(p, 'rb'))) for p in images[i:i + MAX_IMAGES]]
        data = {'content': f"**[{version} 변경 이미지 {i+1}~{i+len(files)}]**"}
        r = requests.post(webhook, data=data, files=files)
        print(f"[+] 이미지 전송 상태: {r.status_code}")
