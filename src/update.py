import os
import zipfile
import shutil
import requests
from pathlib import Path

from mc_config import update_configs
from external_mods import gh_download, modrinth_download

def update_pack(client_dl, server_dl):
    client_zip = os.getcwd() + "\\gtnh-client.zip"
    server_zip = os.getcwd() + "\\gtnh-server.zip"

    if not os.path.exists(client_zip):
        print("[+] Client: " + client_dl)
        grab_zip(client_dl, client_zip)
    else:
        print("[*] Client already downloaded")

    if not os.path.exists(server_zip):
        print("[+] Server: " + server_dl)
        grab_zip(server_dl, server_zip)
    else:
        print("[*] Server already downloaded")


    print("[+] Extracting client")
    with zipfile.ZipFile(client_zip, "r") as zip_ref:
        top_level_path, = zipfile.Path(zip_ref).iterdir()
        client_path = top_level_path.name
        client_path = os.getcwd() + "\\" + client_path

        if os.path.exists(client_path):
            shutil.rmtree(client_path)

        zip_ref.extractall(os.getcwd())

    print("[+] Extracting server")
    with zipfile.ZipFile(server_zip, "r") as zip_ref:
        server_path = os.getcwd() + "\\mc-data"

        if os.path.exists(server_path):
            shutil.rmtree(server_path)
        os.mkdir(server_path)

        zip_ref.extractall(server_path)

    old_instance = r"C:/Users/tlouk/AppData/Roaming/PrismLauncher/instances/GT New Horizons 2.9.0-beta-3"

    shutil.copytree(old_instance + "\\.minecraft\\saves\\New World", server_path + "\\World")
    copy_persistent_files(old_instance, client_path)
    update_configs(client_path)

    gh_download(client_path + "\\.minecraft\\", "GTNewHorizons/worldedit-gtnh")
    gh_download(server_path, "GTNewHorizons/worldedit-gtnh")
    modrinth_download(client_path + "\\.minecraft\\", "euphoria-patches")
    modrinth_download(client_path + "\\.minecraft\\", "lglegacy")


def grab_zip(url: str, filename: str) -> None:
    r = requests.get(url, allow_redirects=True, stream=True)
    if not r.ok:
        print(f"Failed to download {url}")
        exit(1)

    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192 * 8):
            if chunk:
                f.write(chunk)
                f.flush()
                os.fsync(f.fileno())


def git_latest_daily():
    r = requests.get("https://api.github.com/repos/GTNewHorizons/GTNH-Daily-Builds/releases")
    client_dl = ""
    server_dl = ""
    if r.ok:
        js = r.json()
        for release in js:
            for asset in release["assets"]:
                if "mmcprism-java17" in asset["name"]:
                    client_dl = asset["browser_download_url"]
                elif "server-java17" in asset["name"]:
                    server_dl = asset["browser_download_url"]

    if client_dl == "" or server_dl == "":
        print("[!] Couldn't find the right downloads!")
        exit(1)

    return client_dl, server_dl


def latest_release(beta):
    r = requests.get("https://downloads.gtnewhorizons.com/versions.json")
    client_dl = ""
    server_dl = ""
    if r.ok:
        js = r.json()
        for k,release in js.items():
            if "beta" in release["title"] and not beta:
                continue

            client_dl = release["mmc"]["java17_2XUrl"]
            server_dl = release["server"]["java17_2XUrl"]
            break

    if client_dl == "" or server_dl == "":
        print("[!] Couldn't find the right downloads!")
        exit(1)

    return client_dl, server_dl


def update_instance_cfg(instance_cfg_file: str, macos: bool = False):
    all_lines = []

    if macos:
        java_path = r"/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home/bin/java"
    else:
        java_path = r"C:/Program Files/Zulu/zulu-25/bin/javaw.exe"

    print(f"[+] Updating instance cfg. Java path: {java_path}")

    with open(instance_cfg_file, "r") as ifi:
        all_lines.extend(ifi.readlines())

    with open(instance_cfg_file, "w") as ifo:
        for line in all_lines:
            if line.startswith("OverrideJavaArgs"):
                s = line.replace("false", "true")
                ifo.write(s)
            elif line.startswith("OverrideJavaLocation"):
                s = line.replace("false", "true")
                ifo.write(s)
            elif line.startswith("OverrideMemory"):
                s = line.replace("false", "true")
                ifo.write(s)
            elif line.startswith("totalTimePlayed"):
                s = line.replace(line, "totalTimePlayed=3445429") # 957.06 hours as of 08-Jul-26
                ifo.write(s)
            else:
                ifo.write(line)

        new_args = [
            f"JavaPath={java_path}",
            "JvmArgs=-XX:+UseZGC -XX:+UseCompactObjectHeaders -XX:+ExplicitGCInvokesConcurrent -XX:+ClassUnloadingWithConcurrentMark -XX:+AlwaysPreTouch",
            "MinMemAlloc=8192",
            "MaxMemAlloc=8192",
        ]

        for arg in new_args:
            ifo.write(arg + '\n')


def copy_persistent_files(old_instance: str, new_instance: str):
    for file in [
        "backups",
        "journeymap",
        "resourcepacks",
        "saves",
        "schematics",
        "screenshots",
        "shaderpacks",
        "TCNodeTracker",
        "visualprospecting",
        "BotaniaVars.dat",
        "localconfig.cfg",
        "options.txt",
        "optionsnf.txt",
        "servers.dat",
        "serverutilities",
        "mods/WorldEditCuiFe-v1.0.7-mf-1.7.10-10.13.4.1566.jar",
        "mods/BetterFoliage-MC1.7.10-2.0.17.jar",
        "mods/DynamicSurroundings-1.7.10-1.0.6.4.jar",
        "mods/spark-forge1710-1.10-SNAPSHOT.jar",

        # Config files that aren't shipped with the pack
        "config/shaders.properties",
        "config/vendingmachine/favourites",
        "config/AppliedEnergistics2/AppliedEnergistics2.cfg",
        "config/adventurebackpack.cfg",
        "config/GregTech/Pollution.cfg",
        "config/GregTech/GregTech.cfg",
        "config/findit.cfg",
        "config/lwjgl3ify.cfg",
        "config/StorageDrawers.cfg",
        "config/structurelib.cfg"
    ]:
        file = Path(".minecraft") / Path(file)
        input_path = Path(old_instance) / file
        output_path = Path(new_instance) / file
        if not os.path.exists(input_path):
            print(f"[!] {input_path} does not exist, skipping.")
            continue

        print(f"[*] Copying {file}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if input_path.is_dir():
            shutil.copytree(input_path, output_path, dirs_exist_ok=True)
        else:
            shutil.copy2(input_path, output_path)
