import asyncio
import os
import sys
import time
from random import shuffle

import aiohttp
from dotenv import load_dotenv
from googleapiclient.discovery import build

import morefunc as m

"""
Compared to yt_remdel.py, this one does not detect if a video is
member-exclusive, YouTube Music Premium member-only IDs, and it does not return
the reason for an ID's removal.

Remember that this has limited uses due to the fact that it utilizes the YouTube
API.
"""
load_dotenv()
API_KEY = os.getenv("YOUTUBE_DATA_API_V3")
ACCEPT_LANGUAGE = os.getenv("ACCEPT_LANGUAGE")
USER_AGENT = os.getenv("USER_AGENT")
BATCH_SIZE = 50
HEADERS = {
	"Accept-Language": ACCEPT_LANGUAGE,
	"Connection": "keep-alive",
	"user-agent": USER_AGENT,
}

TEMP_RANGE_START = 1 #1_210_000 5310000
TEMP_RANGE_END = 5_500_000 #4_980_000 5320000

dna = set(m.load_yt_id_file(f"{m.dir_path}/ignore/dna.txt"))


def chunk_list(lst, n):
	"""
	Yield successive n-sized chunks from list.
	"""
	for i in range(0, len(lst), n):
		yield lst[i:i + n]


async def fetch_video_statuses(youtube, video_ids) -> dict:
	"""
	Check video statuses using YouTube API for a batch of IDs.
	"""
	request = youtube.videos().list(
		part="status",
		id=",".join(video_ids)
	)
	response = request.execute()
	statuses = {}
	for item in response.get("items", []):
		yid = item["id"]
		statuses[yid] = item["status"]
	# videos not in `response` are possibly deleted or unavailable
	for yid in video_ids:
		if yid not in statuses:
			statuses[yid] = None
	return statuses


async def is_id_private(id, session) -> bool:
	"""
	Return True if video is private.
	"""
	video_url = m.yt_link_formats[2] + id
	try:
		async with session.get(video_url, headers=HEADERS) as resp:
			if resp.status != 200:
				return True
			text = await resp.text()
			indicators = [" private"]	# note the leading space
			return any(indicator in text for indicator in indicators)
	except Exception:
		return True

async def process_batch(youtube, session, batch_ids) -> list[str]:
	"""
	Process one batch of IDs: check status via API, then filter private videos
	concurrently.
	"""
	statuses = await fetch_video_statuses(youtube, batch_ids)

	del_ids = [id for id, status in statuses.items() if status is None]
	if del_ids:
		print(f"\033[1A\x1b[2K{del_ids}")

	tasks = [is_id_private(vid, session) for vid in del_ids]
	privates = await asyncio.gather(*tasks)

	real_del_ids = [
		id for id, is_private in zip(del_ids, privates) if not is_private
	]

	return real_del_ids


async def main() -> None:
	yt_ids_full = m.load_yt_id_file()
	dna = set(m.load_yt_id_file(f"{m.dir_path}/ignore/dna.txt"))
	range_ids = int(input("Enter number of IDs to process: "))
	already_processed = set()
	youtube = build("youtube", "v3", developerKey=API_KEY)

	async with aiohttp.ClientSession(
		connector=aiohttp.TCPConnector(limit=20)) as session:
		ids_removed = 0
		total_iterations = 0
		while True:
			start = time.time()
			temp = [] + yt_ids_full#[TEMP_RANGE_START:TEMP_RANGE_END]
			shuffle(temp)
			# filter out already processed (preserves shuffled order)
			working_set = [yid for yid in temp if yid not in already_processed]
			if not working_set:
				print("No unprocessed IDs remain.")
				break
			ids_to_check = working_set[:range_ids]

			deleted_all = []
			batches = list(chunk_list(ids_to_check, BATCH_SIZE))

			for batch in batches:
				deleted = await process_batch(youtube, session, batch)
				deleted_all.extend(deleted)

			if not deleted_all:
				print("No deleted IDs found. Stopping.")
				break

			# remove deleted ids from the main list and update the file
			yt_ids_full = [yid for yid in yt_ids_full if yid not in deleted_all]
			# cache survivors
			already_processed.update(set(ids_to_check) - set(deleted_all))

			dna_string = ""
			for yid in deleted_all:
				if yid not in dna:
					dna.add(yid)
					dna_string += f"\n{yid}"
			# append deleted ids to this file
			if dna_string:
				with open(
					f"{m.dir_path}/ignore/dna.txt", "a", encoding="utf-8"
				) as f:
					f.write(dna_string)

			# write to list
			file_path = f"{m.dir_path}/ignore/yt_ids.txt"
			with open(file_path, "w", encoding="utf-8") as f:
				f.write("\n".join(yt_ids_full))

			ids_removed += len(deleted_all)
			total_iterations += 1
			end = time.time()
			m.print_with_timestamp(
				f"{', '.join(deleted_all[:10])}\n"
				f"\tREMOVED THIS PASS: {len(deleted_all)}\n"
				f"\tTOTAL REMOVED: {ids_removed}\n"
				f"\tITERATION: {total_iterations}\n"
				f"\tREMAINING TO CHECK: {len(working_set)}\n"
				f"\tALREADY PROCESSED: {len(already_processed)}\n"
				f"\tDURATION: {end - start:.1f}s\n"
			)
			# comment out this break statement if you want to do another pass
			# automatically (mind the quota though)
			# break

	print(f"Complete. Total removed: {ids_removed}")


if __name__ == "__main__":
	try:
		asyncio.run(main())
	except m.SingleInstanceError:
		print(
			f"Another instance is already running. "
			f"{sys.argv[0].split(chr(92))[-1]}"
		)
		sys.exit(1)
