import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID", "").strip()
OUTPUT = Path("videos.json")

def main():
    if not CHANNEL_ID.startswith("UC"):
        raise ValueError("Missing or invalid YOUTUBE_CHANNEL_ID")

    url = (
        "https://www.youtube.com/feeds/videos.xml"
        f"?channel_id={CHANNEL_ID}"
    )

    request = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "yt": "http://www.youtube.com/xml/schemas/2015",
    }

    existing = []
    if OUTPUT.exists():
        existing = json.loads(OUTPUT.read_text(encoding="utf-8"))

    by_id = {
        item["id"]: item
        for item in existing
        if isinstance(item, dict) and item.get("id")
    }

    for entry in root.findall("atom:entry", ns):
        video_id = entry.findtext("yt:videoId", namespaces=ns)
        title = entry.findtext("atom:title", default="", namespaces=ns)

        if not video_id:
            continue

        previous = by_id.get(video_id, {})
        by_id[video_id] = {
            **previous,
            "id": video_id,
            "title": title,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "topic": previous.get("topic", "כללי"),
            "description": previous.get("description", ""),
            "duration": previous.get("duration", ""),
        }

    OUTPUT.write_text(
        json.dumps(list(by_id.values()), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )

    print(f"Saved {len(by_id)} videos")

if __name__ == "__main__":
    main()
