import requests
import os
import re

def gh_download(instance: str, repo: str):
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
        download_jar(instance, dl_url, repo.split("/")[1])

def modrinth_download(instance: str, mod_id: str):
    r = requests.get(
        url = f"https://api.modrinth.com/v2/project/{mod_id}/version",
        params = {
            "game-version": "[\"1.7.10\"]",
            "include_changelog": "false"
        },
        headers = {
            "User-Agent": "kolatra/gtnh-updater/0.1.0 (kolatra03@gmail.com)"
        }
    )

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

    download_jar(instance, dl_url, mod_id, headers = {
        "User-Agent": "kolatra/gtnh-updater/0.1.0 (kolatra03@gmail.com)"
    })


def download_jar(instance: str, dl_url: str, mod_id: str, headers=None):
    if headers is None:
        headers = {}

    jar_req = requests.get(url=dl_url, headers=headers)
    if not jar_req.ok:
        print(f"[!] {dl_url}")
        return

    mod_path = instance + "\\mods\\" + mod_id + ".jar"
    with open(mod_path, "wb") as f:
        for chunk in jar_req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
                os.fsync(f.fileno())

    print(f"[+] Downloaded {mod_id} to {mod_path}")


