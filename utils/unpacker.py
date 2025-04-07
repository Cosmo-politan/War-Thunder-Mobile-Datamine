import os
import subprocess
import filecmp

def unpack_apk(apk_path: str, output_dir: str):
    """APK 파일을 7z로 언팩"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    subprocess.run(["7z", "x", apk_path, f"-o{output_dir}"], check=True)

def generate_changelog(prev_dir, new_dir):
    """이전/현재 디렉터리 비교하여 changelog 및 변경 이미지 목록 생성"""
    changes = []
    changed_images = []

    for dirpath, _, filenames in os.walk(new_dir):
        for f in filenames:
            rel_path = os.path.relpath(os.path.join(dirpath, f), new_dir)
            old_file = os.path.join(prev_dir, rel_path)
            new_file = os.path.join(new_dir, rel_path)

            if not os.path.exists(old_file):
                changes.append(f"+ 추가됨: {rel_path}")
                if f.lower().endswith((".png", ".jpg", ".jpeg")):
                    changed_images.append(new_file)
            elif not filecmp.cmp(old_file, new_file, shallow=False):
                changes.append(f"~ 변경됨: {rel_path}")
                if f.lower().endswith((".png", ".jpg", ".jpeg")):
                    changed_images.append(new_file)

    return "\n".join(changes), changed_images
