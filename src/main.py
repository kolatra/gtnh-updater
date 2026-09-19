import platform
import re
import shutil
from pathlib import Path
from datetime import datetime
import os

from update import update_pack, update_instance_cfg, latest_release
from installs import MacBookAir, DebianServer


def find_existing() -> str:
    for f in Path(os.getcwd()).iterdir():
        if re.compile(r"GT New Horizons.*").search(str(f)) is not None:
            print("[*] Instance is prepared for use!")
            return str(f)

    print("[+] Downloading and preparing brand new client...")
    client_dl, server_dl = latest_release(beta=False)
    update_pack(client_dl, server_dl)

    print("[+] Preparing the server")
    shutil.rmtree(server_path + "/config")
    shutil.rmtree(server_path + "/serverutilities")
    shutil.copytree(client_path + "/.minecraft" + "/config", server_path + "/config")
    shutil.copytree(client_path + "/.minecraft" + "/serverutilities", server_path + "/serverutilities")

    return find_existing()


if __name__ == "__main__":
    if platform.system() != "Windows":
        print(f"[!] {platform.system()}")
        exit(0)

    client_path = find_existing()
    server_path = str(Path(os.getcwd()) / "mc-data")
    instance_name = client_path.split("\\")[-1]
    instance_cfg_file = client_path + "\\instance.cfg"

    update_instance_cfg(instance_cfg_file)
    print("[+] Copying instance to local Prism...")
    win_instances = Path(r"C:/Users/tlouk/AppData/Roaming/PrismLauncher/instances")
    try:
        shutil.copytree(client_path, win_instances / instance_name)
    except FileExistsError:
        print("[!] Failed as this version already exists")

    server_conn = DebianServer()
    server_conn.run_cmd(f"mv /srv/minecraft/gtnh/mc-data /hdd/personal/gtnh-museum/mc-data-{datetime.now().isoformat()}")
    server_conn.copy_file(server_path, server_conn.directory)
    server_conn.run_cmd("ls -a /srv/minecraft/gtnh/mc-data")

    # set instance cfg for macOS
    print("[+] Preparing for macOS copy...")
    macbook_conn = MacBookAir()
    update_instance_cfg(instance_cfg_file, True)
    macbook_conn.run_cmd("brew update && brew upgrade")
    macbook_conn.copy_file(client_path, macbook_conn.directory)

