#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final Integrated Automation Pipeline for War Thunder Mobile

포함 기능:
1. APK 자동 다운로드 및 압축 해제
2. .vromfs.bin 파일 언팩 (wt_tools 자동 클론 및 실행)
3. .blkx.json 파일 파싱을 통한 vehicleName 및 성능 수치 비교
4. .png 이미지 파일 변경(추가/수정) 감지 (예시: 파일 크기 기준 비교)
5. 한/영 changelog 자동 생성 (성능, 이미지 변경 내역 포함)
6. Discord Webhook 전송:
   - 메시지 텍스트는 1900자 기준 자동 분할 전송
   - 이미지 파일은 10장씩 묶어 전송
7. Git 자동 commit 및 push
8. .github/workflows/update.yml 파일 자동 생성 (GitHub Actions 워크플로우)
"""

import os
import re
import zipfile
import requests
import shutil
import subprocess
import datetime
import json
import textwrap
import hashlib
from pathlib import Path
from PIL import Image

# Configuration (Webhook URL는 실제 값을 사용)
CONFIG = {
    'apk_url': 'https://wtmobile.com/apk',
    'download_dir': 'downloads',
    'extract_dir': 'extracted',
    'unpacked_dir': 'unpacked',
    'previous_dir': 'previous',
    'current_dir': 'current',
    'changelog_dir': 'changelogs',
    'images_dir': 'images',
    'diffs_dir': 'diffs',
    'webhook_url': 'https://discord.com/api/webhooks/1358669581388087470/Q3JgZ7kM-0tDQn4UOU7h9UC8y2Sb_lXNBujY8OjHz1tN04_zXwPDR1pB0VE3PjXL-IE0',
    'languages': ['ko', 'en']
}

#######################
# Utility & Setup
#######################
def setup_dirs():
    # CONFIG에 명시된 디렉터리와 언어별 changelog, diffs 폴더 생성
    for key in ['download_dir', 'extract_dir', 'unpacked_dir', 'previous_dir', 'current_dir', 'changelog_dir', 'images_dir', 'diffs_dir']:
        os.makedirs(CONFIG[key], exist_ok=True)
    for lang in CONFIG['languages']:
        os.makedirs(os.path.join(CONFIG['changelog_dir'], lang), exist_ok=True)

def write_update_yml():
    # GitHub Actions 워크플로우 파일 자동 생성 (.github/workflows/update.yml)
    yml_content = textwrap.dedent("""\
        name: Auto Update War Thunder Mobile

        on:
          schedule:
            - cron: "0 3 * * *"
          workflow_dispatch:

        jobs:
          build:
            runs-on: ubuntu-latest
            steps:
              - name: Checkout
                uses: actions/checkout@v3

              - name: Set up Python
                uses: actions/setup-python@v4
                with:
                  python-version: "3.11"

              - name: Install dependencies
                run: pip install requests Pillow

              - name: Run script
                run: python wtm_pipeline_final_with_png.py

              - name: Commit & Push
                run: |
                  git config user.name "github-actions[bot]"
                  git config user.email "github-actions[bot]@users.noreply.github.com"
                  git add .
                  git commit -m "Auto update"
                  git push
    """)
    os.makedirs(".github/workflows", exist_ok=True)
    with open(".github/workflows/update.yml", "w", encoding="utf-8") as f:
        f.write(yml_content)

def print_status(msg):
    # 간단한 상태 출력용 함수
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

#######################
# APK & Unpacking
#######################
def extract_apk_url(html):
    # 간단한 정규식으로 .apk URL 추출
    match = re.search(r'href=[\'"]([^\'"]+\.apk)[\'"]', html)
    if match:
        href = match.group(1)
        return href if href.startswith("http") else CONFIG['apk_url'].rsplit('/', 1)[0] + "/" + href
    return None

def extract_version(url):
    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', url)
    return match.group(1) if match else datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

def download_apk():
    print_status("APK 다운로드 시작...")
    resp = requests.get(CONFIG['apk_url'])
    apk_url = extract_apk_url(resp.text)
    if not apk_url:
        raise Exception("APK 다운로드 링크를 찾을 수 없음.")
    version = extract_version(apk_url)
    apk_path = os.path.join(CONFIG['download_dir'], f"wtm_{version}.apk")
    if os.path.exists(apk_path):
        print_status(f"이미 APK {version} 다운로드됨.")
        return apk_path, version
    r = requests.get(apk_url, stream=True)
    os.makedirs(CONFIG['download_dir'], exist_ok=True)
    with open(apk_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print_status(f"APK 다운로드 완료: {apk_path}")
    return apk_path, version

def unzip_apk(apk_path, version):
    print_status("APK 압축 해제 시작...")
    extract_path = os.path.join(CONFIG['extract_dir'], version)
    with zipfile.ZipFile(apk_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    print_status(f"APK 압축 해제 완료: {extract_path}")
    return extract_path

def clone_wt_tools():
    if not os.path.exists("wt_tools"):
        print_status("wt_tools 클론 중...")
        subprocess.run(["git", "clone", "https://github.com/gszabi99/War-Thunder-Mobile-Datamine.git", "wt_tools"], check=True)
    else:
        print_status("wt_tools 업데이트 중...")
        subprocess.run(["git", "-C", "wt_tools", "pull"], check=True)

def unpack_vromfs(extract_path, version):
    print_status("vromfs.bin 파일 언팩 시작...")
    unpack_path = os.path.join(CONFIG['unpacked_dir'], version)
    os.makedirs(unpack_path, exist_ok=True)
    clone_wt_tools()
    # extract all vromfs.bin files found and unpack them using wt_tools/vromfs_unpacker.py
    for root, _, files in os.walk(extract_path):
        for file in files:
            if file.endswith("vromfs.bin"):
                vromfs_file = os.path.join(root, file)
                print_status(f"언팩: {vromfs_file}")
                subprocess.run(["python3", "wt_tools/vromfs_unpacker.py", vromfs_file, "-o", unpack_path], check=True)
    print_status(f"vromfs 언팩 완료: {unpack_path}")
    return unpack_path

#######################
# .blkx & .png 비교
#######################
def parse_blkx_dir(dir_path):
    # .blkx.json 파일에서 vehicleName 등 성능 데이터를 추출 (파일명 규칙: *.blkx.json)
    blkx_data = {}
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".blkx.json"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        name = data.get("vehicleName", file.replace(".blkx.json", ""))
                        blkx_data[name] = data
                except Exception as e:
                    print_status(f"blkx 파싱 오류: {path} ({e})")
                    continue
    return blkx_data

def compare_blkx(prev_data, curr_data):
    # 이전과 현재의 .blkx 데이터를 비교하여 성능 변화 추출
    changes = {}
    for name, curr in curr_data.items():
        prev = prev_data.get(name)
        if not prev:
            continue
        diff = {}
        for k in curr:
            # 단순 수치 또는 문자열 비교 (필요에 따라 확장 가능)
            if k in prev and curr[k] != prev[k] and isinstance(curr[k], (int, float, str)):
                diff[k] = (prev[k], curr[k])
        if diff:
            changes[name] = diff
    return changes

def parse_png_dir(dir_path):
    # .png 파일 목록을 dictionary 형태(파일 경로 : md5 해시)로 반환
    png_files = {}
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.lower().endswith(".png"):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "rb") as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    png_files[os.path.relpath(full_path, dir_path)] = (full_path, file_hash)
                except Exception as e:
                    print_status(f"PNG 파일 해시 계산 오류: {full_path} ({e})")
    return png_files

def compare_png(prev_files, curr_files):
    # 이전 vs 현재 .png 파일 목록 비교: 추가, 삭제, 수정된 이미지 추출
    changes = {'added': [], 'removed': [], 'modified': []}
    prev_keys = set(prev_files.keys())
    curr_keys = set(curr_files.keys())
    changes['added'] = list(curr_keys - prev_keys)
    changes['removed'] = list(prev_keys - curr_keys)
    for key in prev_keys & curr_keys:
        if prev_files[key][1] != curr_files[key][1]:
            changes['modified'].append(key)
    return changes

#######################
# Discord Webhook & Git
#######################
def send_to_discord(text, images=None):
    webhook_url = CONFIG['webhook_url']
    max_len = 1900
    # 텍스트 메시지 자동 분할 전송
    chunks = [text[i:i+max_len] for i in range(0, len(text), max_len)]
    for chunk in chunks:
        requests.post(webhook_url, json={"content": chunk})
    # 이미지 파일들 10장씩 묶어서 전송
    if images:
        batch_size = 10
        for i in range(0, len(images), batch_size):
            files = []
            for img_path in images[i:i+batch_size]:
                if os.path.exists(img_path):
                    files.append(('file', (os.path.basename(img_path), open(img_path, 'rb'))))
            if files:
                requests.post(webhook_url, files=files)

def auto_commit(version):
    print_status("Git commit & push 시작...")
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"])
    subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"Auto update {version}"], check=True)
    subprocess.run(["git", "push"], check=True)
    print_status("Git commit & push 완료.")

#######################
# Changelog 생성 (blkx & png 변화 포함)
#######################
def format_blkx_changes(changes, lang="en"):
    # vehicle 성능 변화 내역
    header = "[장비 성능 변경]" if lang == "ko" else "[Vehicle Stat Changes]"
    lines = [header]
    for name, diff in changes.items():
        lines.append(f"• {name}")
        for k, (old, new) in diff.items():
            lines.append(f"  - {k}: {old} → {new}")
    return "\n".join(lines)

def format_png_changes(changes, lang="en"):
    # png 이미지 변화 내역
    header = "[이미지 변경]" if lang == "ko" else "[Image Changes]"
    lines = [header]
    if changes['added']:
        lines.append("  [추가된 이미지]")
        for path in changes['added']:
            lines.append(f"    - {path}")
    if changes['removed']:
        lines.append("  [삭제된 이미지]")
        for path in changes['removed']:
            lines.append(f"    - {path}")
    if changes['modified']:
        lines.append("  [변경된 이미지]")
        for path in changes['modified']:
            lines.append(f"    - {path}")
    return "\n".join(lines)

def save_changelog(text, lang, version):
    path = os.path.join(CONFIG['changelog_dir'], lang, f"{version}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

#######################
# Main Pipeline
#######################
def main():
    setup_dirs()
    print_status("자동화 파이프라인 시작")
    
    # APK 다운로드 및 압축 해제
    apk_path, version = download_apk()
    extract_path = unzip_apk(apk_path, version)
    
    # vromfs.bin 언팩 (wt_tools 활용)
    unpack_path = unpack_vromfs(extract_path, version)
    
    # 이전/current 버전 관리
    if os.path.exists(CONFIG['previous_dir']):
        shutil.rmtree(CONFIG['previous_dir'])
    if os.path.exists(CONFIG['current_dir']):
        shutil.move(CONFIG['current_dir'], CONFIG['previous_dir'])
    shutil.copytree(unpack_path, CONFIG['current_dir'])
    
    # .blkx 변경 비교
    prev_blkx = parse_blkx_dir(CONFIG['previous_dir']) if os.path.exists(CONFIG['previous_dir']) else {}
    curr_blkx = parse_blkx_dir(CONFIG['current_dir'])
    blkx_changes = compare_blkx(prev_blkx, curr_blkx)
    
    # .png 파일 비교 (예시: 파일 해시로 비교)
    prev_png = parse_png_dir(CONFIG['previous_dir']) if os.path.exists(CONFIG['previous_dir']) else {}
    curr_png = parse_png_dir(CONFIG['current_dir'])
    png_changes = compare_png(prev_png, curr_png)
    
    # 다국어 changelog 생성 및 Discord 전송
    for lang in CONFIG['languages']:
        # blkx changelog
        blkx_text = format_blkx_changes(blkx_changes, lang)
        # png changelog
        png_text = format_png_changes(png_changes, lang)
        # 최종 changelog 결합
        final_changelog = f"{blkx_text}\n\n{png_text}"
        save_changelog(final_changelog, lang, version)
        send_to_discord(final_changelog)
    
    # Git 자동 commit & push
    auto_commit(version)
    
    # GitHub Actions 워크플로우 파일 자동 생성
    write_update_yml()
    
    print_status("자동화 파이프라인 완료.")

if __name__ == "__main__":
    main()
'''

with open("/mnt/data/wtm_pipeline_final_with_png.py", "w", encoding="utf-8") as f:
    f.write(final_script_code)

# 최종 스크립트 파일 경로 출력
print("/mnt/data/wtm_pipeline_final_with_png.py")
