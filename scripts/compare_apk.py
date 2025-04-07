import os
import difflib

def list_files(directory):
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            full_path = os.path.relpath(os.path.join(root, file), directory)
            file_list.append(full_path)
    return sorted(file_list)

def compare_versions(old_dir, new_dir):
    old_files = list_files(old_dir)
    new_files = list_files(new_dir)

    diff = difflib.unified_diff(old_files, new_files, fromfile='Old APK', tofile='New APK', lineterm='')
    return '\n'.join(diff)

if __name__ == "__main__":
    old_dir = "previous_extracted_apk"
    new_dir = "extracted_apk"

    print("[*] Comparing APK contents...")
    result = compare_versions(old_dir, new_dir)

    if result:
        with open("changelog.txt", "w", encoding="utf-8") as f:
            f.write(result)
        print("[+] Changelog written to changelog.txt")
    else:
        print("[=] No difference found.")
