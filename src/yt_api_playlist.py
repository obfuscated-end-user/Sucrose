import ctypes
import os
import sys

import morefunc as m

from re import search
from collections import OrderedDict
from dotenv import load_dotenv
from googleapiclient.discovery import build

if __name__ == "__main__":
	try:
		instance = m.SingleInstance(port=2)

		load_dotenv()
		API_KEY = os.getenv("YOUTUBE_DATA_API_V3")
		YOUTUBE_API_SERVICE_NAME = "youtube"
		YOUTUBE_API_VERSION = "v3"
		OVERALL = 0

		yt = build(
			YOUTUBE_API_SERVICE_NAME,
			YOUTUBE_API_VERSION,
			developerKey=API_KEY
		)
		dni = [] # do not include
		dupe_del = [] # deleted, but currently in list
		yt_ids_list = m.load_yt_id_file()
		ctypes.windll.kernel32.SetConsoleTitleW("Add YouTube video IDs by playlist IDs")

		def get_ids_from_playlist(youtube, items, pl_id):
			global OVERALL
			try:
				print(f"{m.bcolors.WARNING}This might take a while...{m.bcolors.ENDC}")
				response1 = items.list(
					part="snippet",
					playlistId=pl_id,
					maxResults=50
				)

				# whoaly shiiit 2 API calls, 2 quota points wasted goddamn
				request = youtube.playlists().list(
					part="snippet",
					id=pl_id,
					fields="items(snippet(title))"
				)
				response2 = request.execute()

				if "items" in response2 and len(response2["items"]) > 0:
					print(
						f"TITLE: {m.bcolors.OKGREEN}"
						f"{response2['items'][0]['snippet']['title']}"
						f"{m.bcolors.ENDC}"
					)
				display_str = ""
				# use these ids to test (subject to change)
				# PLbYN2TAnooBC2_cdkh8_CdwEEwrE-9i7B - 1 id
				# PLdJu4NMc51MDvmXeRiUykpy7Ujy9UaNAk - 1 id
				# PLNtcigB9Mc_IElsxqFKHNmkTSQD7ESB-b - 5 ids
				# Deleted video (DUPE)
				counter = 1
				while response1:
					pl_items_list_response = response1.execute()
					for pl_item in pl_items_list_response["items"]:
						vid_id = pl_item["snippet"]["resourceId"]["videoId"]
						if vid_id not in yt_ids_list:
							if pl_item["snippet"]["title"] == "Deleted video":
								display_str = (
									f"{counter}. {m.bcolors.FAIL}{vid_id}"
									f"{m.bcolors.ENDC} - {m.bcolors.FAIL}"
									f"(DELETED){m.bcolors.ENDC}"
								)
								print(display_str)
								dni.append(vid_id)
							elif pl_item["snippet"]["title"] == "Private video":
								display_str = (
									f"{counter}. {m.bcolors.WARNING}{vid_id}"
									f"{m.bcolors.ENDC} - {m.bcolors.WARNING}"
									f"(PRIVATE){m.bcolors.ENDC}"
								)
								print(display_str)
								# because private videos may become public later?
								# dni.append(vid_id)
							else:
								display_str = (
									f"{counter}. {m.bcolors.OKGREEN}{vid_id}"
									f"{m.bcolors.ENDC} - {m.bcolors.OKBLUE}"
									f"{pl_item['snippet']['title']}{m.bcolors.ENDC}"
								)
								print(display_str)
						else:
							# already in list
							display_str = (
								f"{counter}. {m.bcolors.FAIL}{vid_id}"
								f"{m.bcolors.ENDC} - {m.bcolors.HEADER}"
								f"{pl_item['snippet']['title']}{m.bcolors.ENDC}"
								f" {m.bcolors.OKCYAN}(DUPE){m.bcolors.ENDC}"
							)
							# this will only fail if a video has the exact same
							# string on the title
							dupe_del_string = (
								f"- {m.bcolors.HEADER}Deleted video"
								f"{m.bcolors.ENDC} {m.bcolors.OKCYAN}"
								f"(DUPE){m.bcolors.ENDC}"
							)
							if dupe_del_string in display_str:
								dupe_del.append(vid_id)
							print(display_str)
						counter += 1
						yield vid_id
					response1 = youtube.playlistItems().list_next(
						response1,
						pl_items_list_response
					)
					OVERALL = counter - 1
				if dupe_del:
					temp = ""
					if len(dupe_del) == 1:
						temp = f"({dupe_del[0]}\\n)"
					else:
						temp1 = "(" + "".join([f"{id}\\n|" for id in dupe_del])
						temp = temp1[:-1] + ")"
					print(f"\n{m.bcolors.WARNING}REMOVE THESE!{m.bcolors.ENDC}")
					print(f"{m.bcolors.FAIL}{temp}{m.bcolors.ENDC}")
				dupe_del.clear()
				print(
					f"{m.bcolors.WARNING}"
					f"Appending IDs... (DO NOT EXIT WINDOW UNTIL NEXT PROMPT!)"
					f"{m.bcolors.ENDC}"
				)
			except Exception as e:
				print(f"DETAILS:\n{e}")

		input_pl = ""
		while input_pl != "n":
			csi = 1	# clear screen indicator
			try:
				items = yt.playlistItems()
				input_pl = input(
					f"{m.bcolors.OKBLUE}"
					f"Enter a valid playlist URL or ID (type \"n\" to exit): "
					f"{m.bcolors.ENDC}"
				)
				print(m.ERASE_ABOVE.strip(), end="")
				match = search(m.YT_PLAYLIST_ID_REGEX, input_pl)
				while match is not None:
					if csi == 5:
						os.system("cls" if os.name == "nt" else "clear")
						csi = 1
					print(
						f"{m.bcolors.HEADER}"
						f"Number of interactions before clear screen (up to 5):"
						f" {m.bcolors.ENDC}{m.bcolors.FAIL}{csi}{m.bcolors.ENDC}"
					)
					included_id_count = 0
					pl = list(
						OrderedDict.fromkeys(
							get_ids_from_playlist(yt, items, match.groups()[0])
						)
					)
					for vid_id in pl:
						if vid_id not in yt_ids_list:
							with open(
								f"{m.dir_path}/ignore/yt_ids.txt", "a"
							) as yt_id:
								if vid_id not in dni:
									yt_id.write(f"\n{vid_id}")
									included_id_count += 1 # maybe inaccurate
					print(
						f"{m.bcolors.WARNING}{m.ERASE_ABOVE}"
						f"Done! Number of IDs appended: "
						f"{included_id_count}/{OVERALL} ("
						f"{100 * float(included_id_count)/float(OVERALL):.2f}%)"
						f"{m.bcolors.ENDC}"
					)
					yt_ids_list = m.load_yt_id_file()
					input_pl = input(
						f"{m.bcolors.OKBLUE}"
						f"Enter a valid playlist URL/ID (type \"n\" to exit):"
						f" {m.bcolors.ENDC}"
					)
					match = search(m.YT_PLAYLIST_ID_REGEX, input_pl)
					csi += 1
					OVERALL = 0
					# this breaks `csi`, fix later
					print(m.ERASE_ABOVE.strip(), end="")
			except Exception as e:
				print(f"{m.bcolors.FAIL}DETAILS:\n{e}{m.bcolors.ENDC}")

		instance.stop()
	except m.SingleInstanceError:
		print(f"Another instance is already running. {sys.argv[0].split(chr(92))[-1]}")
		sys.exit(1)
