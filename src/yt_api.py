import os
import re
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
API_KEY = os.getenv("YOUTUBE_DATA_API_V3")
dir_path = os.path.dirname(os.path.realpath(__file__))

DEVELOPER_KEY = API_KEY
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

youtube = build("youtube", "v3", developerKey=DEVELOPER_KEY)

def get_videos_from_playlist(youtube, items, playlist_id):
    try:
        print("This might take a while...")
        response = items.list(part="snippet", playlistId=playlist_id)
        while response:
            pl_items_list_response = response.execute()

            for pl_item in pl_items_list_response["items"]:
                video_id = pl_item["snippet"]["resourceId"]["videoId"]
                yield video_id

            response = youtube.playlistItems().list_next(
                response, pl_items_list_response
            )
        print("Done!")
    except Exception as e:
        print("12560129686")
        print(f"DETAILS:\n{e}")

# (?:http|https|)(?::\/\/|)(?:www.|)(?:youtu\.be\/|youtube\.com(?:\/embed\/|\/v\/|\/watch\?v=|\/ytscreeningroom\?v=|\/feeds\/api\/videos\/|\/user\S*[^\w\-\s]|\S*[^\w\-\s]))([\w\-]{12,})[a-z0-9;:@#?&%=+\/\$_.-]*
# [\w\-_]{41}|[\w\-_]{34}|[\w\-_]{18}
# ([\w\-_]{41}|[\w\-_]{34}|[\w\-_]{18})
# only works with ids for the moment
# (?:(?<=[https://])|(?<=[www.youtube.com])|(?<=[playlist])|(?<=[?list])|(?<=[=]))([\w\-_]{41}|[\w\-_]{34}|[\w\-_]{18})
try:
    items = youtube.playlistItems()
    # band-aid solution
    input_playlist = input("Enter a playlist ID: ").strip("https://www.youtube.com/playlist?list=")
    playlist_url_regex = "([\w\-_]{41}|[\w\-_]{34}|[\w\-_]{18})"
    match = re.match(playlist_url_regex, input_playlist)
    print(f"{match}")
    while match is not None:
        playlist = get_videos_from_playlist(youtube, items, input_playlist)
        for video_id in playlist:
            with open(f"{dir_path}/yt_ids.txt", "a") as yt_id:
                yt_id.write(f"\n{video_id}")
        input_playlist = input("Enter a playlist ID: ")
except Exception as e:
    print("12560129686")
    print(f"DETAILS:\n{e}")

"""
https://youtu.be/th5_9woFJmk
https://youtu.be/coZbOM6E47I
https://github.com/CoreyMSchafer/code_snippets/blob/master/Python/YouTube-API/02-Playlist-Duration/playlist.py

example playlists
https://youtube.com/playlist?list=PLmxT2pVYo5LB5EzTPZGfFN0c2GDiSXgQe
https://youtube.com/playlist?list=PLx5dM5qaGDFO-CujeLnLsZ9C4Jsu1gpcM
https://youtube.com/playlist?list=PLDXCaTsLZ6xga_ummU8HCdVQ5R2DuDXHS
https://youtube.com/playlist?list=PLv3TTBr1W_9tppikBxAE_G6qjWdBljBHJ - LONG
https://youtube.com/playlist?list=PLylTVsqZiRXOlDr8PemE5hUTVMGZrLD7G
https://youtube.com/playlist?list=PL19E79A0638C8D449 - weird format
https://youtube.com/playlist?list=PL69BE3BF7D0BB69C4
https://youtube.com/playlist?list=OLAK5uy_mUsMBsIavotUhSOoGSC-I0rzpXAhFAwv4 - does not start with "PL"

these work:
https://www.youtube.com/playlist?list=PLKo9UD3uKyyEW8dG08lLLYBDbZGdtTQNQ

but not these (\the ids themselves work):
https://www.youtube.com/playlist?list=PL3KPNhFywXJe7DTrvp57mkM5Mw6Xaj1xZ
https://www.youtube.com/playlist?list=PLSIxbPZbq9G475HSpPifjdLZO6kCXIGl-
https://www.youtube.com/playlist?list=PLWKjhJtqVAbluXJKKbCIb4xd7fcRkpzoz
"""
