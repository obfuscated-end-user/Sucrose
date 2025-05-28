import ctypes
import morefunc as m
from random import shuffle
from collections import OrderedDict

ctypes.windll.kernel32.SetConsoleTitleW("Remove duplicate IDs")
yt_ids_list = m.load_yt_id_file()

dupes = m.find_dupes(1)

no_dupes = list(OrderedDict.fromkeys(yt_ids_list))
no_dupes_sorted = sorted(no_dupes)

yt_ids_list_shuffle = yt_ids_list
shuffle(yt_ids_list_shuffle)

def add_ids(path, ids):
    with open(path, "w") as f:
        for id in ids:
            if id == ids[-1]:
                f.write(id)
            else:
                f.write(f"{id}\n")


add_ids(f"{m.dir_path}/ignore/yt_ids.txt", no_dupes)
add_ids(f"{m.dir_path}/ignore/yt_ids_sorted.txt", no_dupes_sorted)
add_ids(f"{m.dir_path}/all_ids.txt", yt_ids_list_shuffle)

input("Done! (press enter to exit) ")
