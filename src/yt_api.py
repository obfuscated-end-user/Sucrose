import os
import re
from collections import defaultdict
from collections import OrderedDict
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
API_KEY = os.getenv("YOUTUBE_DATA_API_V3")
dir_path = os.path.dirname(os.path.realpath(__file__))

DEVELOPER_KEY = API_KEY
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

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

yt_vid_ids_file = open(f"{dir_path}/yt_ids.txt", "r")
yt_vid_ids_file_list = [line.strip().split("\n") for line in yt_vid_ids_file.readlines()]
yt_vid_ids_file_list = [id for [id] in yt_vid_ids_file_list]
yt_vid_ids_file.close()

youtube = build("youtube", YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

def get_videos_from_playlist(youtube, items, playlist_id):
    try:
        print(f"{bcolors.WARNING}This might take a while...{bcolors.ENDC}")
        response = items.list(part="snippet", playlistId=playlist_id)
        while response:
            pl_items_list_response = response.execute()
            for pl_item in pl_items_list_response["items"]:
                video_id = pl_item["snippet"]["resourceId"]["videoId"]
                if video_id not in yt_vid_ids_file_list:
                    print(f"{bcolors.OKGREEN}{video_id}{bcolors.ENDC} - {bcolors.UNDERLINE}{bcolors.OKBLUE}{pl_item['snippet']['title']}{bcolors.ENDC}")
                else:
                    print(f"{bcolors.OKGREEN}{video_id}{bcolors.ENDC} - {bcolors.UNDERLINE}{bcolors.HEADER}{pl_item['snippet']['title']}{bcolors.ENDC} {bcolors.FAIL}(DUPE){bcolors.ENDC}")
                yield video_id
            response = youtube.playlistItems().list_next(
                response, pl_items_list_response
            )
        print(f"{bcolors.WARNING}Done!{bcolors.ENDC}")
    except Exception as e:
        print(f"DETAILS:\n{e}")

try:
    items = youtube.playlistItems()
    input_playlist = input(f"{bcolors.HEADER}Enter a valid playlist URL or ID: {bcolors.ENDC}")
    playlist_url_regex = "([\w-]{41}|[\w-]{34}|[\w-]{18})"
    match = re.search(playlist_url_regex, input_playlist)
    while match is not None:
        playlist = list(OrderedDict.fromkeys(get_videos_from_playlist(youtube, items, match.groups()[0])))
        for video_id in playlist:
            if video_id not in yt_vid_ids_file_list:
                with open(f"{dir_path}/yt_ids.txt", "a") as yt_id:
                    yt_id.write(f"\n{video_id}")
        yt_vid_ids_file = open(f"{dir_path}/yt_ids.txt", "r")
        yt_vid_ids_file_list = [line.strip().split("\n") for line in yt_vid_ids_file.readlines()]
        yt_vid_ids_file_list = [id for [id] in yt_vid_ids_file_list]
        yt_vid_ids_file.close()
        input_playlist = input(f"{bcolors.HEADER}Enter a valid playlist URL or ID: {bcolors.ENDC}")
        match = re.search(playlist_url_regex, input_playlist)
except Exception as e:
    print(f"{bcolors.FAIL}DETAILS:\n{e}{bcolors.ENDC}")
