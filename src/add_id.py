import ctypes
import morefunc as m
import re
import sys
from datetime import datetime
from random import choice

if __name__ == "__main__":
	try:
		instance = m.SingleInstance(port=1)

		ctypes.windll.kernel32.SetConsoleTitleW("Add YouTube IDs")
		yt_ids_list = m.load_yt_id_file()

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
				if (id not in yt_ids_list):
					with open(f"{m.dir_path}/ignore/yt_ids.txt", "a") as file:
						file.write(f"\n{id}")
						yt_ids_list.append(id)
						print(
							(f"{m.bcolors.HEADER}{datetime.now().strftime(m.DATE_FORMAT)}{m.bcolors.ENDC} "
							f"{m.bcolors.UNDERLINE}{m.bcolors.OKBLUE}{id}{m.bcolors.ENDC}{m.bcolors.OKGREEN} "
							f"(#{yt_ids_list.index(id) + 1}) added.{m.bcolors.ENDC}")
						)
				else:
					print(
						(f"{m.bcolors.HEADER}{datetime.now().strftime(m.DATE_FORMAT)}{m.bcolors.ENDC} "
						f"{m.bcolors.UNDERLINE}{m.bcolors.OKBLUE}{id}{m.bcolors.ENDC}{m.bcolors.WARNING} already exists"
						f" at line {yt_ids_list.index(id) + 1}.{m.bcolors.ENDC}")
					)
			else:
				print(
					(f"{m.bcolors.HEADER}{datetime.now().strftime(m.DATE_FORMAT)}{m.bcolors.ENDC} "
					f"{m.bcolors.UNDERLINE}{m.bcolors.OKBLUE}{id}{m.bcolors.ENDC}{m.bcolors.FAIL} "
					f"is not a valid YouTube ID.{m.bcolors.ENDC}")
				)


		def id_exists(id: str):
			for line in yt_ids_list:
				if id in line:
					return True
				return False


		dupes = m.find_dupes(0)
		yt_id_regex = re.compile("(?:(?<=^)|(?<==)|(?<=/))([\w_\-]{11})(?=(&|$))")

		continue_add = "y"
		while continue_add != "n":
			try:
				input_id = yt_id_regex.search(input(
					f"{m.bcolors.OKCYAN}Enter a valid YouTube ID/link: {m.bcolors.ENDC}")
				).group(1)
				print(m.ERASE_ABOVE.strip(), end="")
				while re.match(m.YT_VIDEO_ID_REGEX, input_id) is not None:
					if not id_exists(input_id):
						add_id(input_id)
					input_id = yt_id_regex.search(input(
						f"{m.bcolors.OKCYAN}Enter a valid YouTube ID/link: {m.bcolors.ENDC}")
					).group(1)
					print(m.ERASE_ABOVE.strip(), end="")
			except:
				continue_add = input(
					(f"{m.bcolors.HEADER}{datetime.now().strftime(m.DATE_FORMAT)}{m.bcolors.ENDC} "
					f"{m.bcolors.FAIL}Something wrong occurred. Type \"n\" "
					f"to exit, anything else to continue: {m.bcolors.ENDC}")
				).lower()

		instance.stop()
	except m.SingleInstanceError:
		# chr(92) is a backslash
		print(
			f"Another instance is already running. "
			f"{sys.argv[0].split(chr(92))[-1]}"
		)
		sys.exit(1)
