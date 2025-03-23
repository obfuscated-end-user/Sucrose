import os
from collections import defaultdict
from collections import OrderedDict

dir_path = os.path.dirname(os.path.realpath(__file__))

yt_vid_ids_file = open(f"{dir_path}/yt_ids.txt", "r")
yt_vid_ids_file_list = [line.strip().split("\n") for line in yt_vid_ids_file.readlines()]
yt_vid_ids_file_list = [id for [id] in yt_vid_ids_file_list]
yt_vid_ids_file.close()

duplicates = defaultdict(list)
for i, item in enumerate(yt_vid_ids_file_list):
    duplicates[item].append(i + 1)
duplicates = { key:value for key,value in duplicates.items() if len(value) > 1 }

for key, value in duplicates.items():
    print(f"{key}: {value}")

no_dupes = list(OrderedDict.fromkeys(yt_vid_ids_file_list))
with open(f"{dir_path}/yt_ids.txt", "w") as f:
    for id in no_dupes:
        if id == no_dupes[-1]:
            f.write(id)
        else:
            f.write(f"{id}\n")

input("done! (press enter to exit) ")
