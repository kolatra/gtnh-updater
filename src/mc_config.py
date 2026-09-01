from pathlib import Path
import os

def update_configs(new_instance):
    print("[*] Updating configs")

    cfg_changes = {
        "config/AppliedEnergistics2/AppliedEnergistics2.cfg": [("UsageMultiplier=10.0", "UsageMultiplier=1.0")],

        "config/adventurebackpack.cfg": [('"Enable Tools Cycling"=true', '"Enable Tools Cycling"=false')],

        "config/GregTech/Pollution.cfg": [('"Activate Pollution"=true', '"Activate Pollution"=false')],
        "config/GregTech/GregTech.cfg": [
            ("B:machineFireExplosions=true",    "B:machineFireExplosions=false"),
            ("B:machineRainExplosions=true",    "B:machineRainExplosions=false"),
            ("B:machineFlammable=true",         "B:machineFlammable=false"),
            ("B:machineThunderExplosions=true", "B:machineThunderExplosions=false"),
            ("B:machineWireFire=true",          "B:machineWireFire=false")
        ],

        "config/findit.cfg": [("S:SearchRadius=16", "S:SearchRadius=64")],

        "config/lwjgl3ify.cfg": [("B:borderless=false", "B:borderless=true")],

        "config/StorageDrawers.cfg": [
            ("maxDrawers=50", "maxDrawers=500"),
            ("range=4", "range=12")
        ],

        "config/structurelib.cfg": [
            ('I:autoPlaceBudget=25', 'I:autoPlaceBudget=200'),
            ('I:autoPlaceInterval=300', 'I:autoPlaceInterval=1')
        ],

        "serverutilities/serverutilities.cfg": [
            ('backup_timer=0.5', 'backup_timer=0.25'),
            ("backups_to_keep=12", "backups_to_keep=24"),
            ("back=false", "back=true"),
            ("home=false", "home=true"),
            ("tpa=false", "tpa=true"),
            ("nick=false", "nick=true"),
            ("warp=false", "warp=true"),
            (
                """# Enables Ranks. [default: true]
            B:enabled=false""", 
                """# Enables Ranks. [default: true]
            B:enabled=true"""),
            ("chunk_claiming=false", "chunk_claiming=true"),
            ("enable_pvp=TRUE", "enable_pvp=FALSE")
        ],
        "serverutilities/server/ranks.txt": [
            ("claims.max_chunks: 100", "claims.max_chunks: 10000"),
            ("chunkloader.max_chunks: 50", "chunkloader.max_chunks: 5000"),
            ("homes.max: 1", "homes.max: 100"),
            ("homes.cross_dim: false", "homes.cross_dim: true"),
        ]
    }

    for f_name, changes in cfg_changes.items():
        file_path = Path(new_instance) / ".minecraft" / f_name
        if not os.path.exists(file_path):
            print(f"[!] Skipping non-existent file {file_path}")
            continue
        content = file_path.read_text(encoding="utf-8")
        for old, new in changes:
            content = content.replace(old, new)
        file_path.write_text(content, encoding="utf-8")
