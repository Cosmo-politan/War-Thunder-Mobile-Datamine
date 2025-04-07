import requests

APK_URL = "https://wtmobile.com/apk"

def download_apk():
    print("[*] Downloading latest APK...")
    r = requests.get(APK_URL)
    with open("wtmobile_latest.apk", "wb") as f:
        f.write(r.content)

if __name__ == "__main__":
    download_apk()
