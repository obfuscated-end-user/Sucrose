import requests

test123 = requests.get("https://www.youtube.com/watch?v=GtcSIucyoFI")
s = requests.Session()

def is_id_available(id):
    """Check if ID is available. Returns True if ID is not available, False otherwise."""
    check = s.get(f"https://youtu.be/{id}")
    indicators = [
        "Video unavailable",
        "This video isn't available anymore",
        "Private video"
    ]
    response = [indicator for indicator in indicators if (indicator in check.text)]
    # print(f"{batch.index(id) + 1}/{len(batch)}: \"https://youtu.be/{id}\" {response}")
    return bool(response)

print(is_id_available("27FsAdjKnIE"))
