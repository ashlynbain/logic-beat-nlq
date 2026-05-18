"""Shared genre detection — order matters (specific genres before broad ones)."""

# First match wins
GENRE_DETECT_ORDER: list[tuple[str, list[str]]] = [
    (
        "lofi",
        ["lo-fi", "lofi", "lo fi", "chillhop", "chill hop", "study beat", "study beats", "dusty"],
    ),
    ("house", ["house", "edm", "dance", "four on the floor", "four-on-the-floor"]),
    ("hiphop", ["trap", "hip hop", "hiphop", "hip-hop", "drill", "boom bap", "boom-bap"]),
    ("pop", ["pop", "radio", "top 40"]),
    (
        "rnb",
        ["rnb", "r&b", "r and b", "rhythm and blues", "neo soul", "neosoul", "soul"],
    ),
]


def detect_genre(prompt: str) -> str:
    lower = prompt.lower()
    for genre, terms in GENRE_DETECT_ORDER:
        if any(term in lower for term in terms):
            return genre
    return "rnb"
