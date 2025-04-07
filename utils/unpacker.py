print("[DEBUG] unpacker.py가 실행됨!")

import os
import subprocess

def unpack_apk(apk_path: str, output_dir: str):
    """APK 파일을 7z로 언팩"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    subprocess.run(["7z", "x", apk_path, f"-o{output_dir}"], check=True)
