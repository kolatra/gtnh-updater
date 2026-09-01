import requests
import os
import re

# Works on GitHub releases only
def download(instance: str, repo: str):
    r = requests.get(f"https://api.github.com/repos/{repo}/releases")
    if not r.ok:
        print(r.status_code)
        return

    js = r.json()
    latest = js[0]
    for asset in latest["assets"]:
        play_jar_re = re.compile(r".*[0-9]\.jar")
        if not play_jar_re.match(asset["browser_download_url"]):
            continue

        dl_url = asset["browser_download_url"]
        jar_req = requests.get(dl_url)
        if not jar_req.ok:
            print(f"[!] {dl_url}")
            return

        s = repo.split("/")
        filename = s[1]
        mod_path = instance + "/.minecraft/mods" + filename
        with open(mod_path, "wb") as f:
            for chunk in jar_req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
        print(f"[+] Downloaded {filename} to {mod_path}")
