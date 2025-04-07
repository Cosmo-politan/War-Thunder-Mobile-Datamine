import filecmp
import os

def generate_changelog(prev_dir, new_dir):
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
