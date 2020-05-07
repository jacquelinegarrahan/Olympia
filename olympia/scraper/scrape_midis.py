import requests
from olympia import ROOT_DIR
from olympia import files, db


# check if the url is a downloadable file
def is_midi(url):
    try:
        h = requests.head(url, allow_redirects=True, verify=False)
        header = h.headers
        content_type = header.get("content-type")
        if "text" in content_type.lower():
            return False
        if "html" in content_type.lower():
            return False
        return True
    except:
        return False


# get midi via request
def get_midi(midi_url):
    # check if midi available
    if is_midi(midi_url):
        # in case requires a referer
        headers = {
            "Referer": midi_url,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        }

        r = requests.get(midi_url, headers=headers, allow_redirects=True)  # create HTTP response object
        if r:
            return r.content
        else:
            return None

    else:
        return None


# get webpage get file page
def get_webpage(midi_url):
    headers = {
        "Referer": midi_url,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    }

    r = requests.get(midi_url, headers=headers, allow_redirects=True)  # create HTTP response object
    if r:
        return r.content
    else:
        return None
