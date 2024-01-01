# https://youtu.be/th5_9woFJmk
# https://youtu.be/coZbOM6E47I
# https://github.com/CoreyMSchafer/code_snippets/blob/master/Python/YouTube-API/02-Playlist-Duration/playlist.py
# https://stackoverflow.com/questions/21289493/youtube-data-api-3-php-how-to-get-more-than-50-video-from-a-channel
# https://stackoverflow.com/questions/18804904/retrieve-all-videos-from-youtube-playlist-using-youtube-v3-api

# example playlists
# https://youtube.com/playlist?list=PLmxT2pVYo5LB5EzTPZGfFN0c2GDiSXgQe
# https://youtube.com/playlist?list=PLx5dM5qaGDFO-CujeLnLsZ9C4Jsu1gpcM
# https://youtube.com/playlist?list=PLDXCaTsLZ6xga_ummU8HCdVQ5R2DuDXHS
# https://youtube.com/playlist?list=PLv3TTBr1W_9tppikBxAE_G6qjWdBljBHJ - LONG
# https://youtube.com/playlist?list=PL19E79A0638C8D449 - weird format
# https://youtube.com/playlist?list=PL69BE3BF7D0BB69C4
# https://youtube.com/playlist?list=OLAK5uy_mUsMBsIavotUhSOoGSC-I0rzpXAhFAwv4 - does not start with "PL"

import os
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
    response = items.list(part="snippet", playlistId=playlist_id)
    while response:
        pl_items_list_response = response.execute()

        for pl_item in pl_items_list_response["items"]:
            video_id = pl_item["snippet"]["resourceId"]["videoId"]
            yield video_id

        response = youtube.playlistItems().list_next(
            response, pl_items_list_response
        )

items = youtube.playlistItems()
playlist = get_videos_from_playlist(youtube, items, "PLx5dM5qaGDFO-CujeLnLsZ9C4Jsu1gpcM")

print("This might take a while...")
for video_id in playlist:
    with open(f"{dir_path}/yt_ids.txt", "a") as yt_id:
        yt_id.write(f"\n{video_id}")
print("Done!")
