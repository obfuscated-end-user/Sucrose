import ctypes
import os
import subprocess
import sys
import time
import re
from collections import OrderedDict
from dotenv import load_dotenv
from googleapiclient.discovery import build
import morefunc as m
from re import search
from datetime import datetime
from collections import deque
import ctypes
import shutil

if __name__ == "__main__":
	try:
		instance = m.SingleInstance(port=1)
		start = time.time()
		load_dotenv()
		API_KEY = os.getenv("YOUTUBE_DATA_API_V3")
		YOUTUBE_API_SERVICE_NAME = "youtube"
		YOUTUBE_API_VERSION = "v3"
		yt = build(
			YOUTUBE_API_SERVICE_NAME,
			YOUTUBE_API_VERSION,
			developerKey=API_KEY
		)

		def load_yt_ids_with_lines(path):
			"""{"id": index}"""
			ids = {}
			with open(path, "r", encoding="utf-8") as f:
				for i, line in enumerate(f, 1):
					id_ = line.strip()
					if id_:
						ids[id_] = i
			return ids


		def deep_getsizeof(obj):
			seen = set()
			size = 0
			queue = deque([obj])

			while queue:
				o = queue.popleft()
				if id(o) in seen:
					continue
				seen.add(id(o))

				size += sys.getsizeof(o)

				if isinstance(o, dict):
					queue.extend(o.keys())
					queue.extend(o.values())
				elif isinstance(o, (list, tuple, set, frozenset, deque)):
					queue.extend(o)
			return size


		def clean_input(prompt=""):
			"""Handles long pasted links without wrapping artifacts."""
			# single-line prompt
			print(prompt, end="", flush=True)
			# let terminal handle input naturally
			result = input()
			# clear prompt line after enter
			print(m.ERASE_ABOVE.strip(), end="")
			return result


		print(f"{m.bcolors.WARNING}Processing IDs list...")
		yt_ids_list = set(m.load_yt_id_file())
		print(m.ERASE_ABOVE.strip(), end="")
		print("Processing indices...")
		yt_ids_index = load_yt_ids_with_lines(f"{m.dir_path}/ignore/yt_ids.txt")
		ctypes.windll.kernel32.SetConsoleTitleW("YouTube ID Manager")
		print(m.ERASE_ABOVE.strip(), end="")
		print("Finding duplicates...")
		dupes = m.find_dupes(0)
		print(
			f"{len(yt_ids_list):,} IDs - {deep_getsizeof(yt_ids_list):,} "
			"bytes in memory loaded."
		)
		end = time.time()
		print(f"Done! Time taken to analyze IDs: {end - start}{m.bcolors.ENDC}")
		print(
			f'{m.bcolors.OKCYAN}Enter YouTube ID/link/playlist ("n" to exit): '
			f"{m.bcolors.ENDC}"
		)

		yt_id_regex = re.compile(
			"(?:(?<=^)|(?<==)|(?<=/))([\w_\-]{11})(?=(&|$))")
		yt_playlist_regex = re.compile(m.YT_PLAYLIST_ID_REGEX)

		"""
		yt_ids_list - the list of ids
		yt_ids_index - dict structured as {"id": line_number/index}
		"""

		def assert_id_list_length():
			with open(f"{m.dir_path}/ignore/yt_ids.txt", "rb") as f:
				num_lines = sum(1 for _ in f)

			return len(yt_ids_list) == num_lines


		def get_ids_from_playlist(youtube, items, pl_id):
			global OVERALL
			global yt_ids_index
			global yt_ids_list
			if not assert_id_list_length():
				print(
					f"{m.bcolors.WARNING}Changes detected in yt_ids.txt, "
					f"reloading...{m.bcolors.ENDC}"
				)
				yt_ids_list = set(m.load_yt_id_file())
				yt_ids_index = load_yt_ids_with_lines(
					f"{m.dir_path}/ignore/yt_ids.txt")
			try:
				print(
					f"{m.bcolors.WARNING}This might take a while..."
					f"{m.bcolors.ENDC}"
				)
				
				# get playlist title
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

				response1 = items.list(
					part="snippet",
					playlistId=pl_id,
					maxResults=50
				)
				display_str = ""
				counter = 1
				dni = []		# do not include
				dupe_del = []	# deleted but currently in list

				while response1:
					pl_response = response1.execute()
					for pl_item in pl_response["items"]:
						yid = pl_item["snippet"]["resourceId"]["videoId"]
						if yid not in yt_ids_list:
							if pl_item["snippet"]["title"] == "Deleted video":
								display_str = (
									f"{counter} {m.bcolors.FAIL}"
									f"{yid}{m.bcolors.ENDC} {m.bcolors.FAIL}"
									f"(DELETED){m.bcolors.ENDC}"
								)
								print(display_str)
								dni.append(yid)
							elif pl_item["snippet"]["title"] == "Private video":
								yt_ids_index[yid] = len(yt_ids_index) + 1
								display_str = (
									f"{counter} {m.bcolors.WARNING}{yid}"
									f"{m.bcolors.ENDC} {m.bcolors.WARNING}"
									f"(PRIVATE){m.bcolors.ENDC}"
									f" {m.bcolors.OKCYAN}"
									f"({yt_ids_index.get(yid)}){m.bcolors.ENDC}"
								)
								print(display_str)
							else:
								yt_ids_index[yid] = len(yt_ids_index) + 1
								display_str = (
									f"{counter} {m.bcolors.OKGREEN}{yid}"
									f"{m.bcolors.ENDC} {m.bcolors.OKBLUE}"
									f"{pl_item['snippet']['title']}"
									f"{m.bcolors.ENDC}"
									f" {m.bcolors.OKCYAN}"
									f"({yt_ids_index.get(yid)}){m.bcolors.ENDC}"
								)
								print(display_str)
						else:
							display_str = (
								f"{counter} {m.bcolors.FAIL}{yid}"
								f"{m.bcolors.ENDC} {m.bcolors.HEADER}"
								f"{pl_item['snippet']['title']}{m.bcolors.ENDC}"
								f" {m.bcolors.OKCYAN}(DUPE, "
								f"{yt_ids_index.get(yid)}){m.bcolors.ENDC}"
							)
							dni.append(yid)
							dupe_del_string = (
								f"{m.bcolors.HEADER}Deleted "
								f"video{m.bcolors.ENDC} {m.bcolors.OKCYAN}"
								f"(DUPE, "
							)
							if dupe_del_string in display_str:
								dupe_del.append(yid)
							print(display_str)

						counter += 1
						if yid not in dni:
							yield yid

					response1 = youtube.playlistItems().list_next(
						response1, pl_response)
					OVERALL = counter - 1

				if dupe_del:
					temp = f"({dupe_del[0]}\\n?)" if len(dupe_del) == 1 \
						else "(" + "".join(
							[f"{id}\\n?|" for id in dupe_del])[:-1] + ")"
					print(f"\n{m.bcolors.WARNING}REMOVE THESE!{m.bcolors.ENDC}")
					print(f"{m.bcolors.FAIL}{temp}{m.bcolors.ENDC}\n")
					subprocess.run(
						"clip", input=temp, check=True, encoding="utf-8")
			except Exception as e:
				print(f"DETAILS:\n{e}")

		# main loop
		continue_input = "y"
		OVERALL = 0
		csi = 1
		while continue_input != "n":
			# print() # don't remove
			input_str = input(
				f"{m.bcolors.HEADER}{datetime.now().strftime(m.DATE_FORMAT)}"
				f"{m.bcolors.ENDC} "
			)
			input_str = re.sub("(&pp|\?si)=[\w%].*", "", input_str)
			if input_str.replace("/", "").rstrip().lower() == "n":
				break
			try:
				print(m.ERASE_ABOVE.strip(), end="")
				# check for playlist id
				playlist_match = yt_playlist_regex.search(input_str)
				if playlist_match:
					start = time.time()
					if csi > 5:
						os.system("cls" if os.name == "nt" else "clear")
						csi = 1
					print(
						f"{m.bcolors.HEADER}# of interactions before screen "
						f"clears (max 5): {m.bcolors.ENDC}{m.bcolors.FAIL}"
						f"{csi}{m.bcolors.ENDC}"
					)
					pl_id = playlist_match.groups()[0]
					items = yt.playlistItems()
					new_ids = []
					included_id_count = 0
					pl = list(OrderedDict.fromkeys(get_ids_from_playlist(
						yt, items, pl_id)))
					print()
					final_write_string = ""
					for yid in pl:
						if yid not in yt_ids_list:
							new_ids.append(yid)
							final_write_string += f"\n{yid}"
							print(
								f"{m.bcolors.WARNING}{m.ERASE_ABOVE}Processing "
								f"{m.bcolors.OKBLUE}{yid}{m.bcolors.ENDC}"
								f"{m.bcolors.WARNING}, DO NOT EXIT!"
								f"{m.bcolors.ENDC}"
							)
							included_id_count += 1
					csi += 1
					if final_write_string:
						with open(f"{m.dir_path}/ignore/yt_ids.txt", "a") as f:
							f.write(final_write_string)
						yt_ids_list.update(new_ids)
					print()
					end = time.time()
					print(
						f"{m.bcolors.WARNING}{m.ERASE_ABOVE}Done! "
						f"{included_id_count}/{OVERALL} ("
						f"{100 * float(included_id_count)/float(OVERALL):.2f}%)"
						f" ({end - start}s){m.bcolors.ENDC}"
					)
					
					continue

				# check for video ID
				video_match = yt_id_regex.search(input_str)
				if video_match:
					yid = video_match.group(1)
					if re.match(m.YT_VIDEO_ID_REGEX, yid):
						if yid not in yt_ids_list:
							with open(
								f"{m.dir_path}/ignore/yt_ids.txt", "a"
							) as f:
								f.write(f"\n{yid}")
							yt_ids_list.add(yid)
							# mandatory compromise
							yt_ids_index[yid] = len(yt_ids_index) + 1
							print(
								f"{m.bcolors.HEADER}"
								f"{datetime.now().strftime(m.DATE_FORMAT)}"
								f"{m.bcolors.ENDC} {m.bcolors.UNDERLINE}"
								f"{m.bcolors.OKBLUE}{yid}{m.bcolors.ENDC}"
								f"{m.bcolors.OKGREEN} ("
								f"{yt_ids_index.get(yid)}){m.bcolors.ENDC}"
							)
						else:
							if not yt_ids_index.get(yid):
								yt_ids_index = load_yt_ids_with_lines(
									f"{m.dir_path}/ignore/yt_ids.txt")
							print(
								f"{m.bcolors.HEADER}"
								f"{datetime.now().strftime(m.DATE_FORMAT)}"
								f"{m.bcolors.ENDC} {m.bcolors.UNDERLINE}"
								f"{m.bcolors.OKBLUE}{yid}{m.bcolors.ENDC}"
								f"{m.bcolors.WARNING} exists at line "
								f"{yt_ids_index.get(yid)}.{m.bcolors.ENDC}"
							)
						continue

			except KeyboardInterrupt:
				print(f"\n{m.bcolors.WARNING}Interrupted.{m.bcolors.ENDC}")
				continue_input = "n"
			except Exception as e:
				print(f"{m.bcolors.FAIL}Error: {e}{m.bcolors.ENDC}")
				# continue_input = input("Continue? (n to exit): ").lower()

		instance.stop()

	except m.SingleInstanceError:
		print(
			f"Another instance is already running. "
			f"{sys.argv[0].split(chr(92))[-1]}"
		)
		sys.exit(1)
