import os import subprocess import requests import sys import mimetypes

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1358669581388087470/Q3JgZ7kM-0tDQn4UOU7h9UC8y2Sb_lXNBujY8OjHz1tN04_zXwPDR1pB0VE3PjXL-IE0"  # 여기에 본인의 Discord Webhook URL 삽입 VROMFS_PATH = "data/curr" PREV_VROMFS_PATH = "data/prev" OUTPUT_DIR = "data/curr_extracted" PREV_OUTPUT_DIR = "data/prev_extracted" ATTACH_LIMIT = 8  # Discord는 한 번에 최대 10개 파일, 메시지당 여유 고려해 8개

MAX_LENGTH = 1900

def extract_images_from_vromfs(source_path, output_dir): print(f"[*] Extracting images from {source_path}...") os.makedirs(output_dir, exist_ok=True) for root, _, files in os.walk(source_path): for file in files: if file.endswith(".vromfs.bin_u"): full_path = os.path.join(root, file) subprocess.run([ "python3", "scripts/wt_unpack.py", full_path, "--output", output_dir ], check=False)

def get_changed_pngs(): diff = subprocess.run([ "diff", "-qr", PREV_OUTPUT_DIR, OUTPUT_DIR ], capture_output=True, text=True)

added, removed, changed = [], [], []
for line in diff.stdout.strip().split("\n"):
    if "Only in" in line and ".png" in line:
        parts = line.split(": ")
        dir_path = parts[0].replace("Only in ", "")
        file_name = parts[1]
        full_path = os.path.join(dir_path.strip(), file_name.strip())
        if dir_path.startswith(PREV_OUTPUT_DIR):
            removed.append(full_path)
        else:
            added.append(full_path)
    elif line.startswith("Files") and ".png" in line:
        files = line.split(" and ")
        changed.append(files[1].split(" differ")[0])
return added, removed, changed

def send_text_diff_to_discord(added, removed, changed): print("[*] Sending text changelog to Discord...") diff_lines = [] for path in added: diff_lines.append(f"+ [ADDED] {path.replace(OUTPUT_DIR + '/', '')}") for path in removed: diff_lines.append(f"- [REMOVED] {path.replace(PREV_OUTPUT_DIR + '/', '')}") for path in changed: diff_lines.append(f"~ [CHANGED] {path.replace(OUTPUT_DIR + '/', '')}")

text = "\n".join(diff_lines)
chunks = [text[i:i + MAX_LENGTH] for i in range(0, len(text), MAX_LENGTH)]
for idx, chunk in enumerate(chunks):
    data = {
        "content": f"**[자동 이미지 변경 로그 - Part {idx + 1}/{len(chunks)}]**\n```diff\n{chunk}\n```"
    }
    r = requests.post(DISCORD_WEBHOOK, json=data)
    print("[*] Status:", r.status_code)

def send_images_to_discord(images): print("[*] Sending changed images to Discord...") batch = [] for img_path in images: if os.path.exists(img_path): batch.append(img_path) if len(batch) == ATTACH_LIMIT: upload_batch(batch) batch = [] if batch: upload_batch(batch)

def upload_batch(batch): files = [] for i, img_path in enumerate(batch): mime = mimetypes.guess_type(img_path)[0] or "application/octet-stream" files.append((f"file{i}", (os.path.basename(img_path), open(img_path, "rb"), mime))) data = { "content": "[변경된 이미지 첨부]" } r = requests.post(DISCORD_WEBHOOK, data=data, files=files) print("[*] Image upload status:", r.status_code)

if name == "main": extract_images_from_vromfs(PREV_VROMFS_PATH, PREV_OUTPUT_DIR) extract_images_from_vromfs(VROMFS_PATH, OUTPUT_DIR) added, removed, changed = get_changed_pngs() send_text_diff_to_discord(added, removed, changed) send_images_to_discord(added + changed)

