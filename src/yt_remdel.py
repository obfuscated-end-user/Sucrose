import asyncio
import aiohttp
import ctypes
import morefunc as m
import os
import sys
from dotenv import load_dotenv
from random import shuffle

if __name__ == "__main__":
    try:
        instance = m.SingleInstance(port=5)

        load_dotenv()
        ctypes.windll.kernel32.SetConsoleTitleW("Check availability of IDs")
        ACCEPT_LANGUAGE = os.getenv("ACCEPT_LANGUAGE")
        HEADERS = {"Accept-Language": ACCEPT_LANGUAGE}
        RANGE = 700

        yt_ids = m.load_yt_id_file()
        shuffle(yt_ids)
        yt_ids = yt_ids[:RANGE]
        deleted_ids = []

        # DO NOT USE (yet)
        async def is_id_available(id: str, session: aiohttp.ClientSession):
            """Check if ID is available. Returns True if ID is not available, False otherwise."""
            # check thumbnail availability
            thumbnail_url = f"https://img.youtube.com/vi/{id}/default.jpg"
            async with session.get(thumbnail_url, headers=HEADERS) as thumb_response:
                TEST123 = f"TMB {id}"
                if thumb_response.status == 404:
                    print(TEST123 + " FADED")
                    return True
                else:
                    print(TEST123)

            video_url = f"https://www.youtube.com/watch?v={id}/"
            async with session.get(video_url, headers=HEADERS) as video_response:
                if video_response.status != 200:
                    return True
                text = await video_response.text()
                TEST456 = f"VID {id}"
                print(TEST456)
                indicators = [
                    # "Video unavailable", # phrase appears too many times on private videos
                    "This video isn't available anymore",
                    "This video has been removed by the uploader",
                    "This video has been removed for violating YouTube's Terms of Service",
                    "This video is no longer available because the YouTube account associated with this video has been terminated.",
                    "This video is no longer available due to a copyright claim by a third party",
                ]

                return any(indicator in text for indicator in indicators)

        async def main():
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20)) as session:
                tasks = [is_id_available(id, session) for id in yt_ids]
                results = await asyncio.gather(*tasks)

                # TEST
                # print something i can easily see in the terminal
                # print("SUPERMASSIVE BLACK HOLE", results, "\nDANI CALIFORNIA", yt_ids)
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

        instance.stop()
    except m.SingleInstanceError:
        print(f"Another instance is already running. {sys.argv[0].split(chr(92))[-1]}")
        sys.exit(1)