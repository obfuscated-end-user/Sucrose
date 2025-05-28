import os
import requests
from collections import defaultdict

dir_path = os.path.dirname(os.path.realpath(__file__))
ERASE_ABOVE = "\033[1A\033[K" # https://en.wikipedia.org/wiki/ANSI_escape_code
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
YT_VIDEO_ID_REGEX = "^([A-Za-z0-9_\-]{11})$"
YT_PLAYLIST_ID_REGEX = "([\w-]{41}|[\w-]{34}|[\w-]{24}|[\w-]{18})"

yt_link_formats = [
    "https://www.youtube.com/watch?v=",
	"http://y2u.be/",
	"http://youtu.be/",
	"https://youtube.com/shorts/",
    "youtu.be/"
]

# HIJACK ID LIST. COMMENT LINE ON yt_bot.py TO DISABLE. FOR DEBUG PURPOSES!
hj = [
    "YxFs1eAEwrU", "bdOGh2q4184", "zIghUDfX2RY", "zRQoBJ73WaY", "Pbkn21NNduc",
    "KaeYczuhDqw", "hjUgEN9kM_U", "A-bCqqSgw1Y", "jNQXAC9IVRw"
]

class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def load_yt_id_file() -> list[str]:
    """Return a list containing YouTube video IDs."""
    with open(f"{dir_path}/ignore/yt_ids.txt", "r") as f:
        yt_ids = [id for [id] in [l.strip().split("\n") for l in f.readlines()]]
    return yt_ids


def is_id_available(id, session: requests.Session, include_private=False) -> bool:
    """Check if ID is available. Returns True if ID is not available, False otherwise."""
    check = session.get(f"https://youtu.be/{id}")
    indicators = [
        "Video unavailable",
        "This video isn't available anymore",
        "Members-only content",
        "Join this channel to get access to members-only content like this video, and other exclusive perks.",
    ]
    if include_private:
        indicators.append("Private video")

    return bool([indicator for indicator in indicators if (indicator in check.text)])


def find_dupes(mode: int) -> dict[str, list]:
    """Find duplicate YouTube video IDs."""
    duplicates = defaultdict(list)
    for i, item in enumerate(load_yt_id_file()):
        if mode == 1:
            print(ERASE_ABOVE, f"line {i}, id {item}")
        duplicates[item].append(i + 1)
    duplicates = {key:value for key,value in duplicates.items() if len(value) > 1}

    for key, value in duplicates.items():
        print(f"{key}: {value}")

    return duplicates


if __name__ == "__main__":
    print("This file is only meant to be imported, not run directly.")
    input("(press enter to exit) ")
