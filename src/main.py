import platform
from update import update_pack, git_latest_daily, latest_release


if __name__ == "__main__":
    if platform.system() != "Windows":
        print("[!] Only runs on Windows, the server and macOS client are managed remotely.")
        exit(0)

    question = input("[?] Do you want to download the latest daily or stable release?\n")
    if question == "daily" or question == "d":
        client_dl, server_dl = git_latest_daily()
    elif question == "stable" or question == "s":
        client_dl, server_dl = latest_release()
    else:
        print("[!] Invalid input")
        exit(0)

    update_pack(client_dl, server_dl)
