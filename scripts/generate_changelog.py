from send_discord import send_to_discord, send_images_to_discord
import glob

if __name__ == "__main__":
    with open("changelog.txt", "r", encoding="utf-8") as f:
        changelog = f.read().strip()

    if not changelog:
        print("[*] No changes detected, nothing to send.")
    else:
        send_to_discord(changelog)

    
    png_files = glob.glob("extracted_diff/**/*.png", recursive=True)
    if png_files:
        send_images_to_discord(png_files)
    else:
        print("[*] No PNG files to send.")
