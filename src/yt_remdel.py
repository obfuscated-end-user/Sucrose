import asyncio
import aiohttp
import ctypes
import morefunc as m
import os
from dotenv import load_dotenv
from random import shuffle

load_dotenv()
ctypes.windll.kernel32.SetConsoleTitleW("Check availability of IDs")
ACCEPT_LANGUAGE = os.getenv("ACCEPT_LANGUAGE")
RANGE = 100

yt_ids = m.load_yt_id_file()
shuffle(yt_ids)
yt_ids = yt_ids[:RANGE]
deleted_ids = []
headers = {"Accept-Language": ACCEPT_LANGUAGE}

# DO NOT USE (yet)
async def is_id_available(id, session: aiohttp.ClientSession, include_private=False):
    """Check if ID is available. Returns True if ID is not available, False otherwise."""
    # check thumbnail availability
    thumbnail_url = f"https://img.youtube.com/vi/{id}/default.jpg"
    async with session.get(thumbnail_url, headers=headers) as thumb_response:
        TEST123 = f"TMB {id}"
        if thumb_response.status == 404:
            print(TEST123 + " FUCKED")
            return True
        else:
            print(TEST123)

    async with session.get(f"https://www.youtube.com/watch?v={id}", headers=headers) as video_response:
        text = await video_response.text()
        TEST456 = f"VID {id}"
        print(TEST456)
        indicators = [
            "Video unavailable",
            "This video isn't available anymore",
        ]
        if include_private:
            indicators.append("Private video")

        """ response = [indicator for indicator in indicators if (indicator in text)]
        return bool(response) """
        return any(indicator in text for indicator in indicators)

async def main():
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=100)) as session:
        tasks = [is_id_available(id, session) for id in yt_ids]
        results = await asyncio.gather(*tasks)

        # TEST
        # print something i can easily see in the terminal
        print("SUPERMASSIVE BLACK HOLE", results, "\nDANI CALIFORNIA", yt_ids)
        # appends false positives for some reason
        # i suspect this has something to do with regions? idk mate leave it as is
        # yt_ids = yt_ids[:RANGE] - maybe something on this line?
        for id, is_deleted in zip(yt_ids, results):
            if is_deleted:
                print(f"{id} deleted")
                deleted_ids.append(id)

print("Please wait...")
asyncio.run(main())
regex = "("
if len(deleted_ids) <= 0:
    regex = "(none)"
elif len(deleted_ids) == 1:
    regex = f"({deleted_ids[0]})"
else:
    for id in deleted_ids:
        regex = regex + f"{id}\\n|"
    regex = regex[:-1] + ")"
    print(regex)

with open(f"{m.dir_path}/ignore/del_id_regex.txt", "w") as f:
    f.write(regex)

input("Done!")
