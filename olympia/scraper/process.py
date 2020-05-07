from bs4 import BeautifulSoup

# METHOD: parse_content
# DESCRIPTION: parses midi world content
def parse_midi_world_content(content):
    soup = BeautifulSoup(content, "lxml")

    songs = []
    for item in soup.find_all("li"):

        if item.span:
            text = item.get_text().split("\n")[0].strip(" - download")
            text = text.split("(")
            title = text[0][:-1]
            artist = text[1].strip(")")

            song = {"title": title, "artist": artist, "url": item.a["href"]}

            songs.append(song)

    return songs


# METHOD: parse_content
# DESCRIPTION: parses midi world content
def parse_free_midi_content(content):
    soup = BeautifulSoup(content, "lxml")

    songs = []
    for item in soup.find_all("li"):

        if item.span:
            text = item.get_text().split("\n")[0].strip(" - download")
            text = text.split("(")
            title = text[0]
            artist = text[1].strip(")")

            song = {"title": title, "artist": artist, "url": item.a["href"]}

            songs.append(song)

    return songs
