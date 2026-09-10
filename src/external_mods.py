import requests
import os
import re

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
        mod_path = instance + "\\mods\\" + filename + ".jar"
        with open(mod_path, "wb") as f:
            for chunk in jar_req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
        print(f"[+] Downloaded {filename} to {mod_path}")

def modrinth_download(instance: str, url: str):
    session = requests.Session()

    session.headers.update({
        "User-Agent": "kolatra/gtnh-updater/0.4 (kolatra03@gmail.com)"
    })

    session.params.update({
        "game-version": "[\"1.7.10\"]",
        "include_changelog": "false"
    })

    r = session.get(url)

    if not r.ok:
        print("[!] Error getting version")
        print(r.text)
        print(r.status_code)
        return

    json_data = r.json()
    dl_url = ""
    for v in json_data:
        if "1.7.10" not in v["game_versions"]:
            continue

        file = v["files"][0]
        dl_url = file["url"]

    if dl_url == "":
        print("[!] Can't get version")
        return

    session.params.update({})

    jar_req = session.get(dl_url)
    if not jar_req.ok:
        print(f"[!] {dl_url}")
        return

    filename = url.split("/")[-2]
    mod_path = instance + "\\mods\\" + filename + ".jar"
    with open(mod_path, "wb") as f:
        for chunk in jar_req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
                os.fsync(f.fileno())

    print(f"[+] Downloaded {filename} to {mod_path}")

