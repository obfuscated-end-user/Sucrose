import requests
import os

# test123 = requests.get("https://www.youtube.com/watch?v=1AZ4Lc5W75I")
ACCEPT_LANGUAGE = os.getenv("ACCEPT_LANGUAGE")
HEADERS = {"Accept-Language": ACCEPT_LANGUAGE}
s = requests.Session()

params = {
    "hl": "en",
    "gl": "us",
    # other params 
}

def is_id_available(id):
    """Check if ID is available. Returns True if ID is not available, False otherwise."""
    check = s.get(f"https://youtu.be/{id}", headers=HEADERS, params=params)
    if "This video is private" in check.text:
        pass
    else:
        indicators = [
            "This video isn't available anymore",
            "This video has been removed by the uploader",
            "This video has been removed for violating YouTube's Terms of Service",
            "This video is no longer available because the YouTube account associated with this video has been terminated.",
        ]
        response = [indicator for indicator in indicators if indicator in check.text]
        # print(f"{batch.index(id) + 1}/{len(batch)}: \"https://youtu.be/{id}\" {response}")
        print(check.text)
        return bool(response)

print()
print(is_id_available("98TyXNPdMRo"))
input()

"""
deleted examples
lIeE_270J4U

"""