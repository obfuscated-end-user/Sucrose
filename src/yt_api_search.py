import ctypes
import os
import sys

import morefunc as m

from dotenv import load_dotenv
from html import unescape
from googleapiclient.discovery import build

if __name__ == "__main__":
	try:
		instance = m.SingleInstance(port=3)
		load_dotenv()
		API_KEY = os.getenv("YOUTUBE_DATA_API_V3")
		YOUTUBE_API_SERVICE_NAME = "youtube"
		YOUTUBE_API_VERSION = "v3"

		ctypes.windll.kernel32.SetConsoleTitleW("Search and immediately add IDs")
		yt = build(
			YOUTUBE_API_SERVICE_NAME,
			YOUTUBE_API_VERSION,
			developerKey=API_KEY
		)
		yt_ids_list = m.load_yt_id_file()

		def search_youtube(youtube, query, max_results=50):
			try:
				# iirc this consumes a shitload of quota
				request = youtube.search().list(
					part="snippet",
					q=query,
					maxResults=max_results,
					type="video"	# filter to only include videos
				)
				response = request.execute()
				
				counter = 1
				for item in response["items"]:
					id = item["id"]["videoId"]
					title = item["snippet"]["title"]
					if id not in yt_ids_list:
						with open(f"{m.dir_path}/ignore/yt_ids.txt", "a") as yt_id:
							yt_id.write(f"\n{id}")
							print(
								f"{counter}. {m.bcolors.OKGREEN}{id}"
								f"{m.bcolors.ENDC} - {m.bcolors.OKBLUE}"
								f"{unescape(title)}{m.bcolors.ENDC}"
							)
					else:
						print(
							f"{counter}. {m.bcolors.OKGREEN}{id}"
							f"{m.bcolors.ENDC} - {m.bcolors.HEADER}"
							f"{unescape(title)}{m.bcolors.ENDC}"
						)
					counter += 1

			except Exception as e:
				print(f"Error: {e}")

		continue_add = "y"
		while continue_add != "n":
			try:
				search_query = input("enter search query: ")
				search_youtube(yt, search_query)
				yt_ids_list = m.load_yt_id_file()
			except Exception as e:
				continue_add = input(
					f"{m.bcolors.FAIL}Something wrong occurred. Type \"n\" to "
					f"exit, anything else to continue: {m.bcolors.ENDC}"
				).lower()

		instance.stop()
	except m.SingleInstanceError:
		print(f"Another instance is already running. {sys.argv[0].split(chr(92))[-1]}")
		sys.exit(1)
