#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, zipfile, requests, shutil, subprocess, datetime, json, hashlib, textwrap
from pathlib import Path
from PIL import Image

CONFIG = {
    'apk_url': 'https://wtmobile.com/apk',
    'download_dir': ' 'downloads',
    'extract_dir': 'extracted',
    'unpacked_dir': 'unpacked',
    'previous_dir': 'previous',
    'current_dir': 'current',
    'changelog_dir': 'changelogs',
    'images_dir': 'images',
    'webhook_url': 'https://discord.com/api/webhooks/1358669581388087470/Q3JgZ7kM-0tDQn4UOU7h9UC8y2Sb_lXNBujY8OjHz1tN04_zXwPDR1pB0VE3PjXL-IE0',
    'languages': ['ko', 'en']
}

def setup_dirs():
    for d in ['download_dir', 'extract_dir', 'unpacked_dir', 'previous_dir', 'current_dir', 'changelog_dir', 'images_dir']:
        os.makedirs(CONFIG[d], exist_ok=True)
    for lang in CONFIG['languages']:
        os.makedirs(os.path.join(CONFIG['changelog_dir'], lang), exist_ok=True)
    os.makedirs(".github/workflows", exist_ok=True)

def extract_apk_url(html):
    match = re.search(r'href=[\'"]([^\'"]+\.apk)[\'"]', html)
    if match:
        return html[:html.find('.apk')+4].split('"')[-1]
    return None

def extract_version(url):
    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', url)
    return match.group(1) if match else datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

def download_apk():
    r = requests.get(CONFIG['apk_url'])
    apk_url = extract_apk_url(r.text)
    version = extract_version(apk_url)
    apk_path = os.path.join(CONFIG['download_dir'], f"{version}.apk")
    if not os.path.exists(apk_path):
        r = requests.get(apk_url, stream=True)
        with open(apk_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return apk_path, version

def unzip_apk(apk_path, version):
    extract_path = os.path.join(CONFIG['extract_dir'], version)
    with zipfile.ZipFile(apk_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    return extract_path

def clone_unpacker():
    if not os.path.exists("wt_tools"):
        subprocess.run(["git", "clone", "https://github.com/gszabi99/War-Thunder-Mobile-Datamine.git", "wt_tools"])
    else:
        subprocess.run(["git", "-C", "wt_tools", "pull"])

def unpack_vromfs(extract_path, version):
    unpack_path = os.path.join(CONFIG['unpacked_dir'], version)
    os.makedirs(unpack_path, exist_ok=True)
    clone_unpacker()
    for root, _, files in os.walk(extract_path):
        for file in files:
            if file.endswith("vromfs.bin"):
                vpath = os.path.join(root, file)
                subprocess.run(["python3", "wt_tools/vromfs_unpacker.py", vpath, "-o", unpack_path])
    return unpack_path

def parse_blkx_json(dir_path):
    result = {}
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".blkx.json"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        name = data.get("vehicleName", file)
                        result[name] = data
                except: continue
    return result

def compare_blkx(prev, curr):
    diff = {}
    for name, data in curr.items():
        if name not in prev: continue
        changes = {}
        for k in data:
            if k in prev[name] and data[k] != prev[name][k]:
                changes[k] = (prev[name][k], data[k])
        if changes:
            diff[name] = changes
    return diff

def parse_png_hashes(path):
    hashes = {}
    for root, _, files in os.walk(path):
        for file in files:
            if file.lower().endswith(".png"):
                full = os.path.join(root, file)
                with open(full, "rb") as f:
                    hashes[os.path.relpath(full, path)] = hashlib.md5(f.read()).hexdigest()
    return hashes

def compare_png(prev, curr):
    result = {"added": [], "removed": [], "modified": []}
    prev_set = set(prev)
    curr_set = set(curr)
    result["added"] = list(curr_set - prev_set)
    result["removed"] = list(prev_set - curr_set)
    result["modified"] = [f for f in prev_set & curr_set if prev[f] != curr[f]]
    return result

def format_changes_blkx(changes, lang="en"):
    h = "[장비 성능 변경]" if lang == "ko" else "[Vehicle Stat Changes]"
    lines = [h]
    for name, diff in changes.items():
        lines.append(f"• {name}")
        for k, (old, new) in diff.items():
            lines.append(f"  - {k}: {old} → {new}")
    return "\n".join(lines)

def format_changes_png(changes, lang="en"):
    lines = ["[이미지 변경]" if lang == "ko" else "[Image Changes]"]
    for k in ["added", "removed", "modified"]:
        if changes[k]:
            label = {"added": "추가됨", "removed": "삭제됨", "modified": "변경됨"}[k] if lang == "ko" else k.capitalize()
            lines.append(f"  [{label}]")
            lines += [f"    - {f}" for f in changes[k]]
    return "\n".join(lines)

def send_to_discord(text, images=None):
    url = CONFIG['webhook_url']
    parts = [text[i:i+1900] for i in range(0, len(text), 1900)]
    for part in parts:
        requests.post(url, json={"content": part})
    if images:
        for i in range(0, len(images), 10):
            files = [('file', (os.path.basename(p), open(p, 'rb'))) for p in images[i:i+10] if os.path.exists(p)]
            if files:
                requests.post(url, files=files)

def save_changelog(text, lang, version):
    path = os.path.join(CONFIG['changelog_dir'], lang, f"{version}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def auto_git_commit(version):
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"])
    subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"Auto update {version}"], check=True)
    subprocess.run(["git", "push"], check=True)

def write_yml():
    os.makedirs(".github/workflows", exist_ok=True)
    with open(".github/workflows/update.yml", "w") as f:
        f.write(textwrap.dedent("""
        name: Auto Update
        on:
          schedule:
            - cron: "0 3 * * *"
          workflow_dispatch:
        jobs:
          run:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v3
              - name: Set up Python
                uses: actions/setup-python@v4
                with:
                  python-version: '3.11'
              - run: pip install requests Pillow
              - run: python wtm_pipeline_final.py
        """))

def main():
    setup_dirs()
    apk_path, version = download_apk()
    extracted = unzip_apk(apk_path, version)
    unpacked = unpack_vromfs(extracted, version)
    if os.path.exists(CONFIG['previous_dir']):
        shutil.rmtree(CONFIG['previous_dir'])
    if os.path.exists(CONFIG['current_dir']):
        shutil.move(CONFIG['current_dir'], CONFIG['previous_dir'])
    shutil.copytree(unpacked, CONFIG['current_dir'])
    prev_blkx = parse_blkx_json(CONFIG['previous_dir']) if os.path.exists(CONFIG['previous_dir']) else {}
    curr_blkx = parse_blkx_json(CONFIG['current_dir'])
    blkx_changes = compare_blkx(prev_blkx, curr_blkx)
    prev_png = parse_png_hashes(CONFIG['previous_dir']) if os.path.exists(CONFIG['previous_dir']) else {}
    curr_png = parse_png_hashes(CONFIG['current_dir'])
    png_changes = compare_png(prev_png, curr_png)
    for lang in CONFIG['languages']:
        full = format_changes_blkx(blkx_changes, lang) + "\n\n" + format_changes_png(png_changes, lang)
        save_changelog(full, lang, version)
        send_to_discord(full)
    auto_git_commit(version)
    write_yml()

if __name__ == "__main__":
    main()
