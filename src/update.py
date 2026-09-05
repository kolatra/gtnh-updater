import os
import zipfile
import shutil
import requests
from pathlib import Path

import mc_config
import external_mods
import installs

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

    client_path = os.getcwd() + "\\GT New Horizons_script"
    server_path = os.getcwd() + "\\mc-data"

    if os.path.exists(server_path):
        os.remove(server_path)
    os.mkdir(server_path)

    print("Extracting client")
    with zipfile.ZipFile(client_zip, "r") as zip_ref:
        zip_ref.extractall(os.getcwd())
    print("Extracting server")
    with zipfile.ZipFile(server_zip, "r") as zip_ref:
        zip_ref.extractall(server_path)

    instance_cfg_file = client_path + "\\instance.cfg"
    copy_persistent_files(
        Path(r"C:\Users\tlouk\AppData\Roaming\PrismLauncher\instances\GTNH 2.8 Twist"),
        Path(client_path)
    )
    mc_config.update_configs(client_path)

    external_mods.download(client_path, "GTNewHorizons/worldedit-gtnh")
    external_mods.download(server_path, "GTNewHorizons/worldedit-gtnh")

    # set instance cfg for macOS
    update_instance_cfg(instance_cfg_file, True)
    macbook_conn = installs.MacBookAir()
    macbook_conn.copy_file(client_path, macbook_conn.directory)

    # re-update instance cfg for windows
    update_instance_cfg(instance_cfg_file, False)
    print("[+] Copying instance to local Prism...")
    win_instances_path = Path(r"C:/Users/tlouk/AppData/Roaming/PrismLauncher/instances")
    shutil.copytree(client_path, win_instances_path)

    # start preparing the server
    print("[+] Copying config from client to server")
    shutil.rmtree(server_path + "/config")
    shutil.rmtree(server_path + "/serverutilities")
    shutil.copytree(client_path + "/.minecraft" + "/config", server_path + "/config")
    shutil.copytree(client_path + "/.minecraft" + "/serverutilities", server_path + "/serverutilities")

    server_conn = installs.DebianServer()
    print("[+] Connecting to server...")

    print("[!] Press enter to confirm these commands on Titan")
    for cmd in server_conn.commands:
        print("    " + cmd)
    inp = input()
    if len(inp) != 0:
        return

    for cmd in server_conn.commands:
        if cmd == "copy-dir":
            server_conn.copy_file(server_path, server_conn.directory)
        else:
            server_conn.run_cmd(cmd)

    print("[*] Complete!")
    print("[*] Be sure to download: https://modrinth.com/mod/euphoria-patches")

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


def latest_release():
    r = requests.get("https://downloads.gtnewhorizons.com/versions.json")
    client_dl = ""
    server_dl = ""
    if r.ok:
        js = r.json()
        for k,release in js.items():
            if "Beta" in release["title"]:
                continue

            client_dl = release["mmc"]["java17_2XUrl"]
            server_dl = release["server"]["java17_2XUrl"]
            break

    if client_dl == "" or server_dl == "":
        print("[!] Couldn't find the right downloads!")
        exit(1)

    return client_dl, server_dl


def update_instance_cfg(instance_cfg_file: str, macos: bool):
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


def copy_persistent_files(old_instance: Path, new_instance: Path):
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
        "mods/laggoggles-mc1.7.10-4.17.0.jar",

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
        input_path = old_instance / file
        output_path = new_instance / file
        if not os.path.exists(input_path):
            print(f"[!] {input_path} does not exist, skipping.")
            continue

        print(f"[*] Copying {file}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if input_path.is_dir():
            shutil.copytree(input_path, output_path, dirs_exist_ok=True)
        else:
            shutil.copy2(input_path, output_path)
