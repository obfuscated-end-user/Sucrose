import asyncio
import ctypes
import os
import sys
import time

import aiohttp
import morefunc as m

from dotenv import load_dotenv
from random import shuffle

def process_ids():
	# like unearthing fossils, this script tries to filter out deleted youtube
	# videos, you know, whatever
	start = time.time()
	instance = m.SingleInstance(port=5)

	load_dotenv()
	ctypes.windll.kernel32.SetConsoleTitleW("Check availability of IDs")
	ACCEPT_LANGUAGE = os.getenv("ACCEPT_LANGUAGE")
	USER_AGENT = os.getenv("USER_AGENT")
	HEADERS = {
		"Accept-Language":	ACCEPT_LANGUAGE,
		"Connection":		"keep-alive",
		"user-agent":		USER_AGENT
	}

	# clear screen
	os.system("cls" if os.name == "nt" else "clear")

	yt_ids_full  = m.load_yt_id_file()
	# keep the old index from the text file just because i want to
	indexed_ids = list(enumerate(yt_ids_full))

	# change this variable if you get frequent timeouts
	# don't use values >2000
	mode = 0
	range_start = "N/A"
	while True:
		try:
			mode = int(input((
				"Enter a mode:\n"
				"1 - Specify a start and end and remove IDs within that range\n"
				"2 - Randomly remove IDs within a range\n"
			)))
			if (mode == 1):
				print("Don't make the gap too large!")
				range_start = int(input("From index: "))
				range_end = int(input("to index: "))
				while (range_end < range_start):
					range_end = int(input("to index: "))
				# stupid way to catch an exception
				indexed_ids[range_end - 1]
				break
			elif (mode == 2):
				range_end = int(
					input("Enter an int (don't make it too large): ")
				)
				break
			elif (mode < 1):
				# these too
				lol = 1 / 0
				break
			elif (mode > 2):
				lol = 1 / 0
				break
		except:
			pass

	if (mode == 1):
		indexed_ids = indexed_ids[range_start:range_end]
	elif (mode == 2):
		shuffle(indexed_ids)
		indexed_ids = indexed_ids[:range_end]
	del_ids = []

	async def is_id_available(
		id: str,
		session: aiohttp.ClientSession
	) -> tuple[bool, str]:
		"""
		Check if ID is available. Returns (True, indicator) if ID is not
		available, (False, "") otherwise.
		"""
		video_url = f"https://www.youtube.com/watch?v={id}/"
		async with session.get(
			video_url,
			headers=HEADERS
		) as video_response:
			if video_response.status != 200:
				return True, f"HTTP Status {video_response.status}"
			text = await video_response.text()
			print(id, m.ERASE_ABOVE.strip())
			# i know this could be made smaller, but having the exact string
			# makes it more, i don't know, fool-proof? youtube doesn't prevent
			# you on making your video title literally say "This video has been
			# removed for violating YouTube's policy on nudity or sexual
			# content".
			indicators = [
				# "Video unavailable", # phrase appears too many times on private videos
				"Join this channel to get access to members-only content like this video, and other exclusive perks.",
				"This video has been removed for violating YouTube's policy on hate speech. Learn more about combating hate speech in your country.",
				"This video has been removed for violating YouTube's policy on harassment and bullying",
				"This video has been removed for violating YouTube's policy on nudity or sexual content",
				"This video is no longer available because the uploader has closed their YouTube account.",
				"This video is no longer available due to a copyright claim by",
				"This video is no longer available because the YouTube account associated with this video has been terminated.",
				"This video has been removed for violating YouTube's Community Guidelines",
				"This video has been removed for violating YouTube's Terms of Service",
				"This video has been removed for violating YouTube's policy on spam, deceptive practices, and scams",
				"This video has been removed for violating YouTube's policy on violent or graphic content",
				"This video has been removed by the uploader",
				"This video isn't available anymore",
				# "This video is unavailable", # this doesn't work
			]

			for indicator in indicators:
				if indicator in text:
					return True, indicator
			return False, ""


	async def is_id_private(
		id: str,
		session: aiohttp.ClientSession
	) -> bool:
		"""
		Check if ID is private.
		"""
		video_url = f"https://www.youtube.com/watch?v={id}/"
		async with session.get(
			video_url,
			headers=HEADERS
		) as video_response:
			if video_response.status != 200:
				return True
			text = await video_response.text()
			print(id, m.ERASE_ABOVE.strip())
			indicators = [
				" private",	# note the space before "private"
				"HTTP Status 500"
			]

			return any(indicator not in text for indicator in indicators)

	del_ids_temp = []
	async def main() -> None:
		async with aiohttp.ClientSession(
			connector=aiohttp.TCPConnector(limit=20)) as session:
			print("Checking if IDs are available...\n")
			t1 = [is_id_available(yid, session) 
				for idx, yid in indexed_ids]
			r1 = await asyncio.gather(*t1)

			print()
			for (idx, yid), (is_deleted, indicator) in zip(indexed_ids, r1):
				if is_deleted:
					del_ids_temp.append((idx, yid, indicator))

			print("Checking if IDs are private...\n")
			t2 = [is_id_private(yid, session)
				for idx, yid, indicator in del_ids_temp]
			r2 = await asyncio.gather(*t2)

			print()
			for (idx, yid, indicator), is_deleted in zip(del_ids_temp, r2):
				if is_deleted:
					del_ids.append((idx, yid, indicator))

	print("Please wait...")
	asyncio.run(main())
	regex = "("
	links = ""
	del_len = len(del_ids)
	# sort by old index so it doesn't look random on markdown
	sorted_del_ids = sorted(del_ids, key=lambda x: x[0])
	if del_len <= 0:
		regex = "(nothing to see here, don't remove anything)"
		links = "1. [(9001) luM6oeCM7Yw](https://youtu.be/dQw4w9WgXcQ)"
	elif del_len == 1:
		regex = f"({del_ids[0][1]}\\n?)"
		links = (
			f"1. [({del_ids[0][0] + 1}) {del_ids[0][1]}]"
			f"(https://youtu.be/{del_ids[0][1]}) **({del_ids[0][2]})**"
		)
	else:
		for idx_in_list, (orig_idx, id, reason) in enumerate(sorted_del_ids):
			regex = regex + f"{id}\\n?|"
			links += (
				f"{idx_in_list + 1}. [({orig_idx + 1}) {id}]"
				f"(https://youtu.be/{id}) **({reason})**\n"
			)
		regex = regex[:-1] + ")"
		print(regex)

	print(sorted_del_ids, del_len, "\n")

	# use this for easy management
	# https://addons.mozilla.org/en-US/firefox/addon/markdown-viewer-chrome
	with open(f"{m.dir_path}/ignore/del_id_regex.md", "w") as f:
		f.write(
			f"Total IDs: **{len(yt_ids_full)}**  \n"
			f"From index **{range_start}** to **{range_end}**"
			f"  \nDeleted IDs: **{del_len}**  \n\n"
			f"```\n{regex}\n```\n`#. (original index) ID (reason)`\n\n\n{links}"
		)

	end = time.time()
	print(
		f"Time taken (in seconds): {end - start}, "
		f"range: {range_start} to {range_end}\nDone!"
	)

	instance.stop()

if __name__ == "__main__":
	try:
		while True:
			process_ids()
			again = input("Do it again? (y/n): ").strip().lower()
			if again not in ("y", "yes"):
				break
	except m.SingleInstanceError:
		print(
			f"Another instance is already running. "
			f"{sys.argv[0].split(chr(92))[-1]}"
		)
		sys.exit(1)