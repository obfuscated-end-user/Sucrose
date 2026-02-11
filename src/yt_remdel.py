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

	TEMP_RANGE_START = 1_000_000 #1_210_000
	TEMP_RANGE_END = 5_310_000 #4_980_000
	yt_ids_full  = m.load_yt_id_file()
	# keep the old index from the text file just because i want to
	indexed_ids = list(enumerate(yt_ids_full))#[TEMP_RANGE_START:TEMP_RANGE_END]
	dna = set(m.load_yt_id_file(f"{m.dir_path}/ignore/dna.txt"))
	already_processed = set()

	# change this variable if you get frequent timeouts
	# don't use values >2000
	mode = 0
	range_start = "N/A"
	while True:
		try:
			mode = int(input(
				"1 - Specify a start and end, and remove IDs within that range\n"
				"2 - Randomly remove IDs within a range\n"
				"3 - Same as mode 2, with automatic removal of those IDs from"
				" the text file, and repeat until no IDs are found\n\nEnter a"
				" mode: "
			))
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
				range_end = int(input("Enter an int (don't make it too large): "))
				break
			elif (mode == 3):
				range_end = int(input("Enter an int (don't make it too large): "))
				break
			elif (mode < 1):
				# these too
				lol = 1 / 0
				break
			elif (mode > 3):
				lol = 1 / 0
				break
		except:
			pass

	if (mode == 1):
		indexed_ids = indexed_ids[range_start:range_end]
		# filter already processed
		indexed_ids = [(idx, yid) for idx, yid in indexed_ids if yid not in already_processed]
	elif (mode == 2 or mode == 3):
		shuffle(indexed_ids)
		indexed_ids = indexed_ids[:range_end]
		# filter already processed
		indexed_ids = [(idx, yid) for idx, yid in indexed_ids if yid not in already_processed]
	del_ids = []

	async def is_id_available(
		yid: str,
		session: aiohttp.ClientSession
	) -> tuple[bool, str]:
		"""
		Check if ID is available. Returns (True, indicator) if ID is not
		available, (False, "") otherwise.
		"""
		video_url = m.yt_link_formats[2] + yid
		async with session.get(
			video_url,
			headers=HEADERS
		) as video_response:
			if video_response.status != 200:
				return True, f"HTTP Status {video_response.status}"
			text = await video_response.text()
			m.print_with_timestamp(f"{yid}{m.ERASE_ABOVE.strip()}")
			# i know this could be made smaller, but having the exact string makes it more, i don't
			# know, fool-proof? youtube doesn't preventyou on making your video title literally say
			# "This video has been removed for violating YouTube's policy on nudity or sexual
			# content".
			# i think the only time that this would be a false flag is that if a video has the exact
			# same title as one of the strings listed here.
			indicators = [
				# "Video unavailable", # phrase appears too many times on private videos
				"This live stream recording is not available.",
				"This video is only available to Music Premium members",
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
		yid: str,
		session: aiohttp.ClientSession
	) -> bool:
		"""
		Check if ID is private.
		"""
		video_url = m.yt_link_formats[2] + yid
		async with session.get(
			video_url,
			headers=HEADERS
		) as video_response:
			if video_response.status != 200:
				return True
			text = await video_response.text()
			m.print_with_timestamp(f"{yid}{m.ERASE_ABOVE.strip()}")
			indicators = [
				" private",	# note the space before "private"
				"HTTP Status 500"
			]

			return any(indicator not in text for indicator in indicators)


	del_ids_temp = []
	async def main() -> None:
		dna_string = ""
		async with aiohttp.ClientSession(
			connector=aiohttp.TCPConnector(limit=50)) as session:
			m.print_with_timestamp("Checking if IDs are available...")
			del_ids_temp.clear()
			t1 = [is_id_available(yid, session) for idx, yid in indexed_ids]
			r1 = await asyncio.gather(*t1)

			for (idx, yid), (is_deleted, indicator) in zip(indexed_ids, r1):
				if is_deleted:
					del_ids_temp.append((idx, yid, indicator))

			m.print_with_timestamp("Checking if IDs are private...")
			t2 = [is_id_private(yid, session) for idx, yid, indicator in del_ids_temp]
			r2 = await asyncio.gather(*t2)

			for (idx, yid, indicator), is_deleted in zip(del_ids_temp, r2):
				if is_deleted:
					del_ids.append((idx, yid, indicator))
					if yid not in dna:
						dna.add(yid)
						dna_string += f"\n{yid}"

			# append deleted ids to this file
			if dna_string:
				with open(f"{m.dir_path}/ignore/dna.txt", "a", encoding="utf-8") as f:
					f.write(dna_string)

	print("Please wait...")
	if mode == 3:
		# NOTE
		# if you want to stop this while running, ALWAYS MAKE SURE that yt_ids.txt is NOT EMPTY
		# before you press CTRL+C!
		# you risk losing the ENTIRE FILE if you fail to do so!
		# don't let incompetence take you over
		# 2025/11/02: use the YouTube API instead?
		ids_removed = 0
		while True:
			del_ids.clear()
			# create fresh working set from current yt_ids_full
			temp = [] + yt_ids_full#[TEMP_RANGE_START:TEMP_RANGE_END]
			shuffle(temp)
			# filter out already processed IDs (preserves shuffle order)
			working_set = [yid for yid in temp if yid not in already_processed]
			if not working_set:
				m.print_with_timestamp("No unprocessed IDs remain.")
				break
			# use indexed version of working_set for original positions
			id_to_original_index = {
				yid: idx + 1 for idx, yid in enumerate(yt_ids_full)}
			ids_to_check = [(id_to_original_index[yid], yid) for yid in working_set[:range_end]]
			# main() specifically made for this mode
			async def main_mode3():
				nonlocal already_processed
				dna_string = ""
				async with aiohttp.ClientSession(
					connector=aiohttp.TCPConnector(limit=50)) as session:
					# check availability
					m.print_with_timestamp("Checking if IDs are available...")
					t1 = [is_id_available(yid, session) for idx, yid in ids_to_check]
					r1 = await asyncio.gather(*t1)

					del_ids_temp = []
					for (idx, yid), (is_deleted, indicator) in zip(ids_to_check, r1):
						if is_deleted:
							del_ids_temp.append((idx, yid, indicator))

					# check private
					if del_ids_temp:
						m.print_with_timestamp("Checking if IDs are private...")
						t2 = [is_id_private(yid, session) for idx, yid, indicator in del_ids_temp]
						r2 = await asyncio.gather(*t2)

						for (idx, yid, indicator), is_private in zip(del_ids_temp, r2):
							# only keep truly deleted (not private)
							if is_private:
								del_ids.append((idx, yid, indicator))
								if yid not in dna:
									dna.add(yid)
									dna_string += f"\n{yid}"

					# update already_processed with survivors from this batch
					batch_ids = set(yid for _, yid in ids_to_check)
					survivors = batch_ids - set(yid for _, yid, _ in del_ids)
					already_processed.update(survivors)

					if dna_string:
						with open(f"{m.dir_path}/ignore/dna.txt", "a", encoding="utf-8") as f:
							f.write(dna_string)

			asyncio.run(main_mode3())

			ids_removed += len(del_ids)
			m.print_with_timestamp(
				f"{del_ids[:20]}\n"
				f"REMOVED IN THIS BATCH: {len(del_ids)}\n"
				f"TOTAL IDS REMOVED: {ids_removed}\n"
				f"REMAINING TO CHECK: {len(working_set)}\n"
				f"ALREADY PROCESSED: {len(already_processed)}"
			)

			if not del_ids:
				break

			# remove deleted IDs from main list (preserving order)
			ids_to_remove = set(yid for _, yid, _ in del_ids)
			yt_ids_full = [yid for yid in yt_ids_full if yid not in ids_to_remove]

			# write updated main file
			with open(f"{m.dir_path}/ignore/yt_ids.txt", "w", encoding="utf-8") as f:
				f.write("\n".join(yt_ids_full))
	else:
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
		for idx_in_list, (orig_idx, yid, reason) in enumerate(sorted_del_ids):
			regex = regex + f"{yid}\\n?|"
			links += (
				f"{idx_in_list + 1}. [({orig_idx + 1}) {yid}]"
				f"(https://youtu.be/{yid}) **({reason})**\n"
			)
		regex = regex[:-1] + ")"

	print(sorted_del_ids[:20], del_len, "\n")

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
		f"range: {range_start} to {range_end}\nDone!\a"
	)

	ctypes.windll.user32.FlashWindow(
		ctypes.windll.user32.GetParent(
			ctypes.windll.kernel32.GetConsoleWindow()),
		True
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
