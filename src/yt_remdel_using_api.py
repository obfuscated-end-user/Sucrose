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

TEMP_RANGE_START = 1_210_000
TEMP_RANGE_END = 4_970_000


def chunk_list(lst, n):
	"""
	Yield successive n-sized chunks from list.
	"""
	for i in range(0, len(lst), n):
		yield lst[i:i + n]


async def fetch_video_statuses(youtube, video_ids):
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
		vid = item["id"]
		statuses[vid] = item["status"]
	# videos not in `response` are possibly deleted or unavailable
	for vid in video_ids:
		if vid not in statuses:
			statuses[vid] = None
	return statuses


async def is_id_private(id, session):
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

async def process_batch(youtube, session, batch_ids):
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


async def main():
	yt_ids_full = m.load_yt_id_file()
	temp = [] + yt_ids_full[TEMP_RANGE_START:TEMP_RANGE_END]
	shuffle(temp)

	os.system("cls" if os.name == "nt" else "clear")
	range_ids = int(input("Enter number of IDs to process: "))
	ids_to_check = temp[:range_ids]

	print()
	youtube = build("youtube", "v3", developerKey=API_KEY)
	async with aiohttp.ClientSession(
		connector=aiohttp.TCPConnector(limit=20)) as session:
		ids_removed = 0
		total_iterations = 0
		while True:
			start = time.time()
			deleted_all = []
			batches = list(chunk_list(ids_to_check, BATCH_SIZE))
			for batch in batches:
				# print(f"\nBATCH\n{batch[:5]}", m.ERASE_ABOVE.strip())
				deleted = await process_batch(youtube, session, batch)
				deleted_all.extend(deleted)

			if not deleted_all:
				print("No more deleted IDs found.")
				os.system("pause")
				break

			# remove deleted ids from the main list and update the file
			yt_ids_full = [vid for vid in yt_ids_full if vid not in deleted_all]
			# print("DELETED\n", deleted_all[:20], len(deleted_all), "\n")
			file_path = f"{m.dir_path}/ignore/yt_ids.txt"
			with open(file_path, "w", encoding="utf-8") as f:
				f.write("\n".join(yt_ids_full))

			ids_removed += len(deleted_all)
			total_iterations += 1
			end = time.time()

			m.print_with_timestamp(
				f"{', '.join(deleted_all[:10])}\n"
				f"\tREMOVED IN THIS BATCH: {len(deleted_all)}\n"
				f"\tTOTAL IDS REMOVED: {ids_removed}\n"
				f"\tITERATION: {total_iterations}\n"
				f"\tDURATION (in seconds): {end - start}\n"
			)

			# comment out this break statement if you want to do another pass
			# automatically (mind the quota though)
			# break

			# update ids_to_check for next iteration (based on updated list)
			yt_ids_full = m.load_yt_id_file()
			temp = [] + yt_ids_full[TEMP_RANGE_START:TEMP_RANGE_END]
			shuffle(temp)
			ids_to_check = temp[:range_ids]

if __name__ == "__main__":
	try:
		asyncio.run(main())
	except m.SingleInstanceError:
		print(
			f"Another instance is already running. "
			f"{sys.argv[0].split(chr(92))[-1]}"
		)
		sys.exit(1)
