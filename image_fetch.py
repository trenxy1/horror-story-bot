"""
Step 4: Pull atmospheric horror-themed stock images from Pexels.
"""
from pathlib import Path
import random
import requests

import config

PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"


def fetch_images(story_id: str, count: int) -> list[Path]:
    if not config.PEXELS_API_KEY:
        raise RuntimeError(
            "PEXELS_API_KEY is not set. Get a free key at https://www.pexels.com/api/"
        )

    headers = {"Authorization": config.PEXELS_API_KEY}
    story_dir = config.IMAGE_DIR / story_id
    story_dir.mkdir(parents=True, exist_ok=True)

    saved_paths = []
    queries = config.IMAGE_SEARCH_QUERIES.copy()
    random.shuffle(queries)

    img_index = 0
    for query in queries:
        if len(saved_paths) >= count:
            break
        per_query = min(4, count - len(saved_paths))
        params = {"query": query, "per_page": per_query, "orientation": "landscape"}
        resp = requests.get(PEXELS_SEARCH_URL, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        photos = resp.json().get("photos", [])

        for photo in photos:
            if len(saved_paths) >= count:
                break
            img_url = photo["src"]["large"]
            img_resp = requests.get(img_url, timeout=30)
            img_resp.raise_for_status()
            img_path = story_dir / f"img_{img_index}.jpg"
            img_path.write_bytes(img_resp.content)
            saved_paths.append(img_path)
            img_index += 1

    if not saved_paths:
        raise RuntimeError("No Pexels images could be fetched for any query")

    return saved_paths


if __name__ == "__main__":
    paths = fetch_images("test_story", count=8)
    print(f"[OK] Downloaded {len(paths)} images:")
    for p in paths:
        print(" -", p)
