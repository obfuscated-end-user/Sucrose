import os
import requests

dir_path = os.path.dirname(os.path.realpath(__file__))
s = requests.Session()

with open(f"{dir_path}/batch.txt", "r") as file:
    batch = [id for [id] in [line.strip().split("\n") for line in file.readlines()]]

def is_id_available(id):
    """Check if ID is available. Returns True if ID is not available, False otherwise."""
    check = s.get(f"https://youtu.be/{id}")
    indicators = [
        "Video unavailable",
        "This video isn't available anymore",
        "Private video"
    ]
    response = [indicator for indicator in indicators if (indicator in check.text)]
    print(f"{batch.index(id) + 1}/{len(batch)}: \"https://youtu.be/{id}\" {response}")
    return bool(response)


for item in batch:
    if is_id_available(item):
        with open(f"{dir_path}/unavailable.txt", "a") as file:
            file.write(f"\n{item}")
