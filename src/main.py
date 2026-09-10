import platform
import re

from update import *


def find_existing():
    gt_instance = re.compile(r"GT New Horizons.*")
    for f in Path(os.getcwd()).iterdir():
        if gt_instance.search(str(f)) is not None:
            print("[*] Instance is prepared for use!")
            return f

    print("[+] Downloading and preparing brand new client...")
    client_dl, server_dl = latest_release(beta=True)
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

    remote_copy = False

    client_path = str(find_existing())
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

    if remote_copy:
        macbook_conn = installs.MacBookAir()
        server_conn = installs.DebianServer()

        # set instance cfg for macOS
        print("[+] Preparing for macOS copy...")
        update_instance_cfg(instance_cfg_file, True)
        macbook_conn.copy_file(client_path, macbook_conn.directory)

        print("[!] Press enter to confirm commands on Titan")
        for cmd in server_conn.commands:
            print("    " + cmd)
        inp = input()
        if len(inp) != 0:
            exit(0)

        for cmd in server_conn.commands:
            if cmd == "copy-dir":
                server_conn.copy_file(server_path, server_conn.directory)
            else:
                server_conn.run_cmd(cmd)

