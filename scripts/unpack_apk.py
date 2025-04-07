import zipfile
import os
import sys

APK_PATH = sys.argv[1] if len(sys.argv) > 1 else "wtmobile_latest.apk"
OUTPUT_DIR = "extracted_apk"

def unpack_apk(apk_path, output_dir):
    print(f"[*] Unpacking: {apk_path}")
    os.makedirs(output_dir, exist_ok=True)
    with zipfile.ZipFile(apk_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    print("[+] APK unpacked successfully.")

if __name__ == "__main__":
    unpack_apk(APK_PATH, OUTPUT_DIR)
