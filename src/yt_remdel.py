import asyncio
import ctypes
import os
import sys
import time

import aiohttp
import morefunc as m

from dotenv import load_dotenv
from random import shuffle

if __name__ == "__main__":
	# like unearthing fossils, this script tries to filter out deleted youtube
	# videos, you know, whatever
	try:
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

		# change this variable if you get frequent timeouts
		# don't use values >2000
		id_range = int(input("enter an int (don't make it too large): "))

		yt_ids = m.load_yt_id_file()
		shuffle(yt_ids)
		yt_ids = yt_ids[:id_range]
		deleted_ids = []

		async def is_id_available(
			id: str,
			session: aiohttp.ClientSession
		) -> bool:
			"""
			Check if ID is available. Returns True if ID is not available, False otherwise.
			"""
			# check thumbnail availability
			thumbnail_url = f"https://img.youtube.com/vi/{id}/default.jpg"
			async with session.get(
				thumbnail_url,
				headers=HEADERS
			) as thumb_response:
				if thumb_response.status == 404:
					return True

			video_url = f"https://www.youtube.com/watch?v={id}/"
			async with session.get(
				video_url,
				headers=HEADERS
			) as video_response:
				if video_response.status != 200:
					return True
				text = await video_response.text()
				print(id, m.ERASE_ABOVE.strip())
				# i know this could be made smaller, but having the exact string
				# makes it more, i don't know, fool-proof? youtube doesn't
				# prevent you on making your video title literally say "This
				# video has been removed for violating YouTube's policy on
				# nudity or sexual content".
				indicators = [
					# "Video unavailable", # phrase appears too many times on private videos
					"This video has been removed for violating YouTube's policy on hate speech. Learn more about combating hate speech in your country.",
					"This video has been removed for violating YouTube's policy on harassment and bullying",
					"This video has been removed for violating YouTube's policy on nudity or sexual content",
					"This video is no longer available because the uploader has closed their YouTube account.",
					"This video is no longer available due to a copyright claim by",
					"This video is no longer available due to a copyright claim by a third party",
					"This video is no longer available because the YouTube account associated with this video has been terminated.",
					"This video has been removed for violating YouTube's Community Guidelines",
					"This video has been removed for violating YouTube's Terms of Service",
					"This video has been removed for violating YouTube's policy on spam, deceptive practices, and scams",
					"This video has been removed for violating YouTube's policy on violent or graphic content",
					"This video has been removed by the uploader",
					"This video is unavailable",
					"This video isn't available anymore",
				]

				return any(indicator in text for indicator in indicators)


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
					" private" # note the space before "private"
				]

				return any(indicator not in text for indicator in indicators)

		deleted_ids_temp = []
		async def main() -> None:
			async with aiohttp.ClientSession(
				connector=aiohttp.TCPConnector(limit=20)) as session:
				print("Checking if IDs are available...\n")
				tasks1 = [is_id_available(id, session) for id in yt_ids]
				results1 = await asyncio.gather(*tasks1)

				print()
				for id, is_deleted in zip(yt_ids, results1):
					if is_deleted:
						print(f"{id} deleted")
						deleted_ids_temp.append(id)

				print("Checking if IDs are private...\n")
				tasks2 = [is_id_private(id, session) for id in deleted_ids_temp]
				results2 = await asyncio.gather(*tasks2)

				print()
				for id, is_deleted in zip(deleted_ids_temp, results2):
					if is_deleted:
						print(f"{id} deleted")
						deleted_ids.append(id)

		print("Please wait...")
		asyncio.run(main())
		regex = "("
		links = ""
		if len(deleted_ids) <= 0:
			regex = "(none)"
			links = "1. [luM6oeCM7Yw](https://youtu.be/dQw4w9WgXcQ)"
		elif len(deleted_ids) == 1:
			regex = f"({deleted_ids[0]}\\n)"
			links = f"1. [{deleted_ids[0]}](https://youtu.be/{deleted_ids[0]})"
		else:
			for idx, id in enumerate(deleted_ids):
				regex = regex + f"{id}\\n|"
				links = links + f"{idx + 1}. [{id}](https://youtu.be/{id})\n"
			regex = regex[:-1] + ")"
			print(regex)

		print("\nTEMP", deleted_ids_temp, len(deleted_ids_temp))
		print("FINAL", deleted_ids, len(deleted_ids), "\n")

		# use this for easy management
		# https://addons.mozilla.org/en-US/firefox/addon/markdown-viewer-chrome
		with open(f"{m.dir_path}/ignore/del_id_regex.md", "w") as f:
			f.write(f"```{regex}```\n\n{links}")

		end = time.time()
		print(f"Time taken (in seconds): {end - start}, id_range: {id_range}")
		input("Done!")

		instance.stop()
	except m.SingleInstanceError:
		print(
			f"Another instance is already running. "
			f"{sys.argv[0].split(chr(92))[-1]}"
		)
		sys.exit(1)
