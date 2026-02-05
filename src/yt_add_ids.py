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
from datetime import datetime
from collections import deque
import ctypes

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
		# do not add list, most of these are member-restricted videos, videos
		# that contain personally identifiable information, etc.
		dna = set(m.load_yt_id_file(f"{m.dir_path}/ignore/dna.txt"))
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
		dna_remove = [yid for yid in yt_ids_list if yid in dna]
		dna_remove_str = f"({dna_remove[0]}\\n?)" if len(dna_remove) == 1 \
			else "(" + "".join(
				[f"{yid}\\n?|" for yid in dna_remove])[:-1] + ")"
		if dna_remove_str != "()":
			print(f"\n{m.bcolors.WARNING}REMOVE THESE!{m.bcolors.ENDC}")
			print(f"{m.bcolors.FAIL}{dna_remove_str}{m.bcolors.ENDC}\n")
			subprocess.run("clip", input=dna_remove_str, check=True, encoding="utf-8")
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


		def process_video_item(yid, pl_item, counter, yt_ids_list, yt_ids_index, dna):
			"""Process single video item and return status dict"""
			global dupe_del, show_remove_msg
			if yid not in yt_ids_list:
				if pl_item["snippet"]["title"] == "Deleted video":
					global dupe_del
					if "dupe_del" not in globals():
						dupe_del = []
					dupe_del.append(yid)
					return {
						"display": f"{counter} {m.bcolors.FAIL}{yid}{m.bcolors.ENDC} {m.bcolors.FAIL}(DELETED){m.bcolors.ENDC}",
						"action": "dni"
					}
				elif pl_item["snippet"]["title"] == "Private video":
					yt_ids_index[yid] = len(yt_ids_index) + 1
					return {
						"display": f"{counter} {m.bcolors.WARNING}{yid}{m.bcolors.ENDC} {m.bcolors.WARNING}(PRIVATE){m.bcolors.ENDC} {m.bcolors.OKCYAN}({yt_ids_index[yid]}){m.bcolors.ENDC}",
						"action": "yield" # this used to be "index" and i was like why tf it doesn't work
					}
				elif yid in dna:
					return {
						"display": f"{counter} {m.bcolors.FAIL}{yid}{m.bcolors.ENDC} {m.bcolors.FAIL}{pl_item['snippet']['title']}{m.bcolors.ENDC} {m.bcolors.FAIL}(SKIPPED){m.bcolors.ENDC}",
						"action": "skip"
					}
				else:
					yt_ids_index[yid] = len(yt_ids_index) + 1
					return {
						"display": f"{counter} {m.bcolors.OKGREEN}{yid}{m.bcolors.ENDC} {m.bcolors.OKBLUE}{pl_item['snippet']['title']}{m.bcolors.ENDC} {m.bcolors.OKCYAN}({yt_ids_index[yid]}){m.bcolors.ENDC}",
						"action": "yield"
					}
			else:
				display_str = f"{counter} {m.bcolors.FAIL}{yid}{m.bcolors.ENDC} {m.bcolors.HEADER}{pl_item['snippet']['title']}{m.bcolors.ENDC} {m.bcolors.WARNING}({yt_ids_index.get(yid)}){m.bcolors.ENDC}"
				dupe_del_string = f"{m.bcolors.HEADER}Deleted video{m.bcolors.ENDC} {m.bcolors.WARNING}("
				if dupe_del_string in display_str:
					if "dupe_del" not in globals():
						dupe_del = []
					dupe_del.append(yid)
					global show_remove_msg
					show_remove_msg = True
				return {"display": display_str, "action": "dni"}


		def print_batch(batch):
			"""Print batch of status lines at once"""
			print("\n".join([item["display"] for item in batch]))


		def get_ids_from_playlist(youtube, items, pl_id):
			global OVERALL
			global yt_ids_index
			global yt_ids_list
			global dna
			global dupe_del
			global show_remove_msg
			show_remove_msg = False
			if not assert_id_list_length():
				print(f"{m.bcolors.WARNING}Changes detected in yt_ids.txt, reloading...{m.bcolors.ENDC}")
				yt_ids_list = set(m.load_yt_id_file())
				yt_ids_index = load_yt_ids_with_lines(f"{m.dir_path}/ignore/yt_ids.txt")
				dna = set(m.load_yt_id_file(f"{m.dir_path}/ignore/dna.txt"))
			try:
				print(f"{m.bcolors.WARNING}This might take a while...{m.bcolors.ENDC}")
				request = youtube.playlists().list(
					part="snippet",
					id=pl_id,
					fields="items(snippet(title))"
				)
				response2 = request.execute()
				if "items" in response2 and len(response2["items"]) > 0:
					print(f"TITLE: {m.bcolors.OKGREEN}{response2['items'][0]['snippet']['title']}{m.bcolors.ENDC}")

				response1 = items.list(part="snippet", playlistId=pl_id, maxResults=50)
				counter = 1
				dni = []
				dupe_del = []
				dna_new = []
				batch_buffer = []
				BATCH_SIZE = 50

				while response1:
					pl_response = response1.execute()
					for pl_item in pl_response["items"]:
						yid = pl_item["snippet"]["resourceId"]["videoId"]
						status_info = process_video_item(yid, pl_item, counter, yt_ids_list, yt_ids_index, dna)
						batch_buffer.append(status_info)
						
						if status_info["action"] == "yield":
							if yid not in dni:
								yield yid
						elif status_info["action"] == "dni":
							dni.append(yid)
						counter += 1
						if len(batch_buffer) >= BATCH_SIZE:
							print_batch(batch_buffer)
							batch_buffer = []
					if batch_buffer:
						print_batch(batch_buffer)
						batch_buffer = []
					response1 = youtube.playlistItems().list_next(response1, pl_response)
					OVERALL = counter - 1

				dna_new = [yid for yid in dupe_del if yid not in dna]
				for yid in dna_new:
					dna.add(yid)
				if dna_new:
					with open(f"{m.dir_path}/ignore/dna.txt", "a") as f:
						f.write("\n" + "\n".join(dna_new))

				if show_remove_msg and dupe_del:
					temp = f"({dupe_del[0]}\\n?)" if len(dupe_del) == 1 \
						else "(" + "".join([f"{yid}\\n?|" for yid in dupe_del])[:-1] + ")"
					print(f"\n{m.bcolors.WARNING}REMOVE THESE!{m.bcolors.ENDC}")
					print(f"{m.bcolors.FAIL}{temp}{m.bcolors.ENDC}\n")
					subprocess.run("clip", input=temp, check=True, encoding="utf-8")

					dna = set(m.load_yt_id_file(f"{m.dir_path}/ignore/dna.txt"))

			except Exception as e:
				print(f"DETAILS:\n{e}")

		# main loop
		continue_input = "y"
		OVERALL = 0
		csi = 1
		while continue_input != "n":
			input_str = input(
				f"{m.bcolors.HEADER}{datetime.now().strftime(m.DATE_FORMAT)}"
				f"{m.bcolors.ENDC} "
			)
			input_str = re.sub("(&pp|\?si)=[\w%].*", "", input_str)
			# skip these because they appear often enough when you do it
			domains = ["facebook.com", "instagram.com", "tiktok.com", "reddit.com", "fandom.com"]
			if any(domain in input_str.lower() for domain in domains):
				print(m.ERASE_ABOVE.strip(), end="")
				continue
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
						if yid in dna:
							print(
								f"{m.bcolors.HEADER}"
								f"{datetime.now().strftime(m.DATE_FORMAT)}"
								f"{m.bcolors.ENDC} {m.bcolors.UNDERLINE}"
								f"{m.bcolors.OKBLUE}{yid}{m.bcolors.ENDC} "
								f"{m.bcolors.FAIL}(SKIPPED){m.bcolors.ENDC}"
							)
						elif yid not in yt_ids_list:
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
								f"{m.bcolors.WARNING} ({yt_ids_index.get(yid)})"
								f"{m.bcolors.ENDC}"
							)
						continue

			except KeyboardInterrupt:
				print(f"\n{m.bcolors.WARNING}Interrupted.{m.bcolors.ENDC}")
				continue_input = "n"
			except Exception as e:
				print(f"{m.bcolors.FAIL}Error: {e}{m.bcolors.ENDC}")

		instance.stop()

	except m.SingleInstanceError:
		print(
			f"Another instance is already running. "
			f"{sys.argv[0].split(chr(92))[-1]}"
		)
		sys.exit(1)
