import math
import os
import random
import re
import requests
import socket
import threading
import time

from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

dir_path = os.path.dirname(os.path.realpath(__file__))
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
ERASE_ABOVE = "\033[1A\x1b[2K" # https://en.wikipedia.org/wiki/ANSI_escape_code
SUCROSE_IMAGE = os.getenv("SUCROSE_IMAGE")
YT_VIDEO_ID_REGEX = "^([A-Za-z0-9_\-]{11})$"
YT_PLAYLIST_ID_REGEX = "([\w-]{41}|[\w-]{34}|[\w-]{24}|[\w-]{18})"

yt_link_formats = [
	"https://www.youtube.com/watch?v=",
	"http://y2u.be/",
	"http://youtu.be/",
	"https://youtube.com/shorts/",
	"youtu.be/"
]

# HIJACK ID LIST. COMMENT LINE ON yt_bot.py TO DISABLE. FOR DEBUG PURPOSES!
hj = [
	"YxFs1eAEwrU", "bdOGh2q4184", "zIghUDfX2RY", "zRQoBJ73WaY", "Pbkn21NNduc",
	"KaeYczuhDqw", "hjUgEN9kM_U", "A-bCqqSgw1Y", "jNQXAC9IVRw", "i8a3gjt_Ar0"
]

class bcolors:
	HEADER = "\033[95m"
	OKBLUE = "\033[94m"
	OKCYAN = "\033[96m"
	OKGREEN = "\033[92m"
	WARNING = "\033[93m"
	FAIL = "\033[91m"
	ENDC = "\033[0m"
	BOLD = "\033[1m"
	UNDERLINE = "\033[4m"


class SingleInstanceError(Exception):
	pass

class SingleInstance:
	def __init__(self, port=86, host="127.0.0.1"):
		self.port = port
		self.host = host
		if not self._check_if_first_instance():
			raise SingleInstanceError("Another instance is already running.")
		self._setup_server()


	def _check_if_first_instance(self) -> bool:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.settimeout(1)
		try:
			sock.connect((self.host, self.port))
			sock.close()
			return False	# already running
		except (ConnectionRefusedError, socket.timeout):
			return True	 # no instance running


	def _setup_server(self) -> None:
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind((self.host, self.port))
		self.sock.listen(1)
		self.running = True
		self.thread = threading.Thread(target=self._listen)
		self.thread.daemon = True
		self.thread.start()


	def _listen(self) -> None:
		while self.running:
			try:
				conn, addr = self.sock.accept()
				conn.close()
			except Exception:
				pass


	def stop(self) -> None:
		self.running = False
		self.sock.close()
		self.thread.join()


def load_yt_id_file(path: str=f"{dir_path}/ignore/yt_ids.txt") -> list[str]:
	"""
	Return a list containing YouTube video IDs.
	"""
	with open(path, "r") as f:
		yt_ids = [l.split("\n")[0] for l in f.readlines()]
	return yt_ids


def is_id_available(
	id: str,
	session: requests.Session,
	include_private: bool=False
) -> bool:
	"""
	Check if ID is available. Returns True if ID is not available, False otherwise.
	"""
	check = session.get(f"https://youtu.be/{id}")
	indicators = [
		"Video unavailable",
		"This video isn't available anymore",
		"Members-only content",
		"Join this channel to get access to members-only content like this video, and other exclusive perks.",
	]
	if include_private:
		indicators.append("Private video")

	return bool(
		[indicator for indicator in indicators if (indicator in check.text)]
	)


def find_dupes(mode: int) -> dict[str, list]:
	"""
	Find duplicate YouTube video IDs.
	"""
	dupes = defaultdict(list)
	for i, item in enumerate(load_yt_id_file()):
		if mode == 1:
			print(ERASE_ABOVE, f"line {i}, id {item}")
		dupes[item].append(i + 1)
	dupes = {key : value for key, value in dupes.items() if len(value) > 1}

	for key, value in dupes.items():
		print(f"{key}: {value}")

	return dupes


def print_with_timestamp(text: str) -> None:
	"""
	Print text into the terminal with a timestamp.
	"""
	print(
		f"{bcolors.HEADER}{datetime.now().strftime(DATE_FORMAT)}"
		f"{bcolors.ENDC} {text}"
	)


def format_duration(s: int) -> str:
	"""
	Formats an int duration in seconds into HH:MM:SS.
	"""
	# 3600s = 1hr
	return time.strftime("%M:%S", time.gmtime(s)) if s < 3600 else time.strftime("%H:%M:%S", time.gmtime(s))


def progress_bar(
	elapsed: int,
	total: int,
	length: int=20
) -> str:
	"""
	Generate a progress bar.
	"""
	# empty bar if duration unknown
	# you can test this by inputting an ongoing youtube livestream link
	if total < 1:
		return "═" * length
	filled_length = int(length * elapsed // total)
	# - 1 because of 🟢
	return "═" * filled_length + "🟢" + "═" * (length - filled_length - 1)


def random_chars(
	chars: str="▁▂▃▄▅▆▇█",
	length: int=20
) -> str:
	"""
	Generate random sequences of chars on a specified length.
	"""
	# .ıilI
	return "".join(random.choice(list(chars)) for _ in range(length))


def wave_chars(
	chars: str="▁▂▃▄▅▆▇█",
	length: int=20,
	cycles: float=1.0,
	noise_level: float=0.1
) -> str:
	"""
	Generate sequences of chars in a way that it somewhat looks wavy. `chars` should be from low to high "frequency".
	"""
	# ai my ass. my explanations are awful.
	res = []
	for i in range(length):
		# https://en.wikipedia.org/wiki/Sine_and_cosine
		# sine produces a range [-1, 1] (square brackets mean inclusive)
		# python expects you to input sine angle in rad, which is covered by pi
		# 2pi is a full circle in rad, multiplied by random noise
		# multiplied by i for each point in the x-axis
		# +1 and /2 are done to normalize it to [0, 1]
		sine_val = (math.sin(2 * math.pi * cycles * i / length) + 1) / 2
		# add random noise to sine wave while limiting it to a valid range
		noisy_val = min(
			max(sine_val + random.uniform(-noise_level, noise_level), 0), 1
		)
		# convert that to an int index
		idx = int(noisy_val * (len(chars) - 1))
		res.append(chars[idx])
	return "".join(res)


def escape_markdown(text: str) -> str:
	"""Escape possible markdown syntax in a string. (UNFINISHED)"""
	escape_chars = r"*`"
	escaped_text = re.sub(f"[{escape_chars}]", r"\\\g<0>", text)
	# escaped_text = sub("[*]", "\*", text)
	return escaped_text


if __name__ == "__main__":
	print("This file is only meant to be imported, not run directly.")
	input("(press Enter to exit) ")
