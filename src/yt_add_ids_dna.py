import ctypes
import os
import sys
import time
import re
import requests
from dotenv import load_dotenv
from googleapiclient.discovery import build
import morefunc as m
from datetime import datetime

"""
How to get ALL members-only content for a YouTube channel:
1. Go to a YouTube channel
2. Click "more" on bold text (near "More about this channel")
3. Scroll down and click "Share channel"
4. Click "Copy Channel ID"
5. Paste the ID here on this url: https://www.youtube.com/playlist?list=ID_HERE
6. Replace the "UC" on the ID part with "UUMO"
	- example: UCdyqAaZDKHXg4Ahi7VENThQ -> UUMOdyqAaZDKHXg4Ahi7VENThQ
	- so the url becomes: https://www.youtube.com/playlist?list=UUMOdyqAaZDKHXg4Ahi7VENThQ
7. If it shows undefined or an error, it means that the channel doesn't have any members-only content
"""

if __name__ == "__main__":
	try:
		instance = m.SingleInstance(port=1337)
		start = time.time()
		load_dotenv()
		API_KEY = os.getenv("YOUTUBE_DATA_API_V3")
		YOUTUBE_API_SERVICE_NAME = "youtube"
		YOUTUBE_API_VERSION = "v3"
		yt = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

		def load_dna():
			"""Load current dna.txt as set"""
			return set(m.load_yt_id_file(f"{m.dir_path}/ignore/dna.txt"))


		def save_dna(new_ids):
			"""Append new unique IDs to dna.txt"""
			if new_ids:
				with open(f"{m.dir_path}/ignore/dna.txt", "a", encoding="utf-8") as f:
					f.write("\n" + "\n".join(new_ids))


		def clean_input(prompt=""):
			"""Handles long pasted links without wrapping artifacts."""
			print(prompt, end="", flush=True)
			result = input()
			print(m.ERASE_ABOVE.strip(), end="")
			return result

		def get_channel_id_from_handle_or_url(input_str, api_key):
			"""Extract channel ID from handle (@username), user/, or channel/ URL"""
			# handle regex for "@username", "user/", "channel/"
			yt_handle_regex = re.compile(r"https://www\.youtube\.com/(?:@|user/|channel/)([\w.%-]+?)/?(?!\S)")
			handle_match = yt_handle_regex.search(input_str)
			if handle_match:
				handle = handle_match.group(1)
				try:
					# now i know i could've used the api here but for some reason, forHandle doesn't work for me
					# using requests, use yt api with channels.list with forHandle parameter
					url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forHandle={handle}&key={api_key}"
					response = requests.get(url)
					data = response.json()
					if data.get("items"):
						return data["items"][0]["id"]
				except Exception:
					pass

			# fallback, check for direct channel ID (UC...)
			yt_channel_id_regex = re.compile(r"UC[\w-]{22}")
			channel_match = yt_channel_id_regex.search(input_str)
			if channel_match:
				return channel_match.group(0)

			return None


		def get_members_playlist_id(channel_id):
			"""Convert channel ID to members-only playlist ID (UUMO...)"""
			if channel_id and channel_id.startswith("UC"):
				return f"UUMO{channel_id[2:]}"
			return None


		def get_playlist_video_ids(playlist_id):
			"""Get all video IDs from members-only playlist"""
			print(f"{m.bcolors.WARNING}Fetching playlist videos...{m.bcolors.ENDC}")
			video_ids = []
			try:
				request = yt.playlistItems().list(part="snippet", playlistId=playlist_id, maxResults=50)
				while request:
					response = request.execute()
					for item in response["items"]:
						video_id = item["snippet"]["resourceId"]["videoId"]
						video_ids.append(video_id)
					request = yt.playlistItems().list_next(request, response)
				return video_ids
			except Exception as e:
				print(f"{m.bcolors.FAIL}Playlist fetch error: {e}{m.bcolors.ENDC}")
				return []

		print(f"{m.bcolors.WARNING}YouTube Excluded IDs Manager loaded...")
		dna = load_dna()
		ctypes.windll.kernel32.SetConsoleTitleW("YouTube Excluded IDs Manager")
		print(m.ERASE_ABOVE.strip(), end="")
		print(f"{len(dna):,} excluded IDs loaded.")

		print(f'{m.bcolors.OKCYAN}Enter YouTube ID/link/channel URL/members-only playlist ("n" to exit): {m.bcolors.ENDC}')

		yt_id_regex = re.compile(r"(?:(?<=^)|(?<==)|(?<=/))([\w-]{11})(?=(&|$|/))")
		yt_channel_id_regex = re.compile("UC[\\w-]{22}")
		members_playlist_regex = re.compile(
			r"(?:list=|(?:^|/)playlist\?list=|(?:^|[^\w]))(UUMO[\w-]{25,}|UUM[\w-]{21,})(?=[&/?\\s]|$)",
			re.IGNORECASE
		)

		while True:
			input_str = clean_input(f"{m.bcolors.HEADER}{datetime.now().strftime(m.DATE_FORMAT)} {m.bcolors.ENDC}")
			if input_str.lower().strip() in ["n", "exit", "quit"]:
				break

			# clean up
			input_str = re.sub(r"(&pp|\\?si)=[\w%-].*", "", input_str)

			# check for members-only playlist first (UUM/UUMO)
			playlist_match = members_playlist_regex.search(input_str)
			if playlist_match:
				pl_id = playlist_match.group(1)
				print(f"{m.bcolors.OKCYAN}Processing members-only playlist: {pl_id}{m.bcolors.ENDC}")

				video_ids = get_playlist_video_ids(pl_id)
				if not video_ids:
					print(f"{m.bcolors.FAIL}No videos found or error accessing playlist{m.bcolors.ENDC}")
					continue

				# filter out existing dna entries and preserve order
				new_ids = []
				seen = set(dna)
				for vid_id in video_ids:
					if vid_id not in seen:
						new_ids.append(vid_id)
						seen.add(vid_id)

				if new_ids:
					save_dna(new_ids)
					dna.update(new_ids)
					print(f"{m.bcolors.OKGREEN}Added {len(new_ids)} new IDs from playlist{m.bcolors.ENDC}")
					print(f"{m.bcolors.OKCYAN}Total excluded IDs: {len(dna):,}{m.bcolors.ENDC}")
				else:
					print(f"{m.bcolors.WARNING}All {len(video_ids)} IDs already excluded{m.bcolors.ENDC}")
				continue

			# check for channel url/handle first
			channel_id = get_channel_id_from_handle_or_url(input_str, API_KEY)
			if channel_id:
				print(f"{m.bcolors.OKCYAN}Found channel ID: {channel_id}{m.bcolors.ENDC}")
				members_pl_id = get_members_playlist_id(channel_id)

				if members_pl_id:
					print(f"{m.bcolors.OKCYAN}Members-only playlist: {members_pl_id}{m.bcolors.ENDC}")
					video_ids = get_playlist_video_ids(members_pl_id)

					if not video_ids:
						print(f"{m.bcolors.WARNING}No members-only videos found for this channel{m.bcolors.ENDC}")
						continue

					# filter out existing dna entries and preserve order
					new_ids = []
					seen = set(dna)
					for vid_id in video_ids:
						if vid_id not in seen:
							new_ids.append(vid_id)
							seen.add(vid_id)

					if new_ids:
						save_dna(new_ids)
						dna.update(new_ids)
						print(f"{m.bcolors.OKGREEN}Added {len(new_ids)} new members-only IDs{m.bcolors.ENDC}")
						print(f"{m.bcolors.OKCYAN}Total excluded IDs: {len(dna):,}{m.bcolors.ENDC}")
					else:
						print(f"{m.bcolors.WARNING}All {len(video_ids)} members-only IDs already excluded{m.bcolors.ENDC}")
				else:
					print(f"{m.bcolors.WARNING}Invalid channel ID format{m.bcolors.ENDC}")
				continue

			# check for single video id
			video_match = yt_id_regex.search(input_str)
			if video_match:
				yid = video_match.group(1)
				if yid in dna:
					print(f"{m.bcolors.OKBLUE}{yid}{m.bcolors.ENDC} {m.bcolors.WARNING}already excluded{m.bcolors.ENDC}")
				else:
					save_dna([yid])
					dna.add(yid)
					print(f"{m.bcolors.OKBLUE}{yid}{m.bcolors.ENDC} {m.bcolors.OKGREEN}EXCLUDED{m.bcolors.ENDC}")
					print(f"{m.bcolors.OKCYAN}Total excluded IDs: {len(dna):,}{m.bcolors.ENDC}")
				continue

			print(f"{m.bcolors.FAIL}No valid YouTube ID, channel URL, or members-only playlist found{m.bcolors.ENDC}")

		print(f"{m.bcolors.OKGREEN}DNA Manager closed. {len(dna):,} total exclusions.{m.bcolors.ENDC}")
		instance.stop()

	except m.SingleInstanceError:
		print(f"DNA Manager already running.")
		sys.exit(1)
	except KeyboardInterrupt:
		print(f"\n{m.bcolors.WARNING}Interrupted.{m.bcolors.ENDC}")
	except Exception as e:
		print(f"{m.bcolors.FAIL}Error: {e}{m.bcolors.ENDC}")
