import ctypes
import morefunc as m
import re
import sys
import time

from datetime import datetime
from random import choice

def generate_url() -> str:
	"""
	Generates a YouTube video link from the list of IDs.
	"""
	return m.yt_link_formats[2] + choice(yt_ids_list)


def add_id(id: str) -> None:
	"""
	Add an ID from the list of IDs.
	"""
	# It's up to you to find patterns in chaos.
	if re.search(m.YT_VIDEO_ID_REGEX, id):
		if id not in yt_ids_list:
			with open(f"{m.dir_path}/ignore/yt_ids.txt", "a") as file:
				file.write(f"\n{id}")
				yt_ids_list.append(id)
				print(
					f"{m.bcolors.HEADER}"
					f"{datetime.now().strftime(m.DATE_FORMAT)}{m.bcolors.ENDC} "
					f"{m.bcolors.UNDERLINE}{m.bcolors.OKBLUE}{id}"
					f"{m.bcolors.ENDC}{m.bcolors.OKGREEN} "
					f"(#{yt_ids_list.index(id) + 1}) added.{m.bcolors.ENDC}"
				)
		else:
			print(
				f"{m.bcolors.HEADER}{datetime.now().strftime(m.DATE_FORMAT)}"
				f"{m.bcolors.ENDC} {m.bcolors.UNDERLINE}{m.bcolors.OKBLUE}{id}"
				f"{m.bcolors.ENDC}{m.bcolors.WARNING} already exists at line "
				f"{yt_ids_list.index(id) + 1}.{m.bcolors.ENDC}"
			)


if __name__ == "__main__":
	try:
		instance = m.SingleInstance(port=1)
		start = time.time()

		ctypes.windll.kernel32.SetConsoleTitleW("Add YouTube IDs")
		yt_ids_list = m.load_yt_id_file()

		dupes = m.find_dupes(0)
		yt_id_regex = re.compile(
			"(?:(?<=^)|(?<==)|(?<=/))([\w_\-]{11})(?=(&|$))"
		)
		end = time.time()
		print(f"time taken to analyze IDs: {end - start}")

		continue_add = "y"
		while continue_add != "n":
			try:
				input_id = yt_id_regex.search(input(
					f"{m.bcolors.OKCYAN}Enter a valid YouTube ID/link: "
					f"{m.bcolors.ENDC}")
				).group(1)
				print(m.ERASE_ABOVE.strip(), end="")
				while re.match(m.YT_VIDEO_ID_REGEX, input_id) is not None:
					if f"\n{input_id}" not in yt_ids_list:
						add_id(input_id)
					input_id = yt_id_regex.search(input(
						f"{m.bcolors.OKCYAN}Enter a valid YouTube ID/link: "
						f"{m.bcolors.ENDC}")
					).group(1)
					print(m.ERASE_ABOVE.strip(), end="")
			except:
				continue_add = input(
					f"{m.bcolors.HEADER}{datetime.now().strftime(m.DATE_FORMAT)}"
					f"{m.bcolors.ENDC} {m.bcolors.FAIL}Something wrong "
					"occurred. Type \"n\" to exit, anything else to continue: "
					f"{m.bcolors.ENDC}"
				).lower()

		instance.stop()
	except m.SingleInstanceError:
		# chr(92) is a backslash
		print(
			f"Another instance is already running. "
			f"{sys.argv[0].split(chr(92))[-1]}"
		)
		sys.exit(1)
