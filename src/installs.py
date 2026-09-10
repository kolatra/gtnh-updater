from fabric import Connection, Config
from datetime import datetime
import subprocess

class ExternalInstall:
    config: Config
    ssh: Connection
    address: str
    username: str
    directory: str

    def __init__(self, address: str, username: str, directory: str):
        self.config = Config()
        self.ssh = Connection(host=address, user=username, config=self.config)
        self.address = address
        self.username = username
        self.directory = directory

    def run_cmd(self, cmd: str):
        print(f"[*] {self.username}@{self.address} > {cmd}")
        self.ssh.run(cmd)

    def copy_file(self, src: str, dst: str):
        cmd = ["scp", "-r", f"{src}", f"{self.username}@{self.address}:{dst}"]
        print("[+] " + " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("[#] Output:", result.stdout)
            print("[#] Error:", result.stderr)
            print("[#] Exit code:", result.returncode)

class MacBookAir(ExternalInstall):
    def __init__(self):
        super().__init__(
            address="MacBook-Air.local",
            username="tyler",
            directory="/Users/tyler/Library/Application Support/PrismLauncher/instances"
        )

class DebianServer(ExternalInstall):
    def __init__(self):
        super().__init__(
            address="192.168.1.64",
            username="tyler",
            directory="/srv/minecraft/gtnh/mc-data"
        )

        self.commands = [
            "mv /srv/minecraft/gtnh/mc-data/World /srv/minecraft/gtnh/temp-work/World",
            f"mv /srv/minecraft/gtnh/mc-data /hdd/personal/gtnh-museum/mc-data-{datetime.now().isoformat()}",
            "copy-dir",
            "mv /srv/minecraft/gtnh/temp-work/World /srv/minecraft/gtnh/mc-data",
            "sed -i -E 's/ nogui/\\ -Dfml.queryResult=confirm nogui/' /srv/minecraft/gtnh/mc-data/startserver-java9.sh",
            "ls -lah /srv/minecraft/gtnh/mc-data"
        ]
