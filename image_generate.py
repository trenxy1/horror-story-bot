"""
Generates AI images tied directly to each scene of the story, using
Pollinations.ai — a free, no-signup, no-API-key image generation service.
Each image's prompt is built from that scene's actual text plus a fixed
style suffix, so every image in a video shares a consistent moody look
AND actually depicts that moment of the story (not generic stock photos).

IMPORTANT: requests are made ONE AT A TIME with spacing between them, and
retry with backoff on 429 (rate limit) errors. Pollinations' free tier
rate-limits aggressively — parallel requests get rejected almost entirely,
which is why an earlier version of this file (using a thread pool) ended up
with nearly every scene failing and falling back to a single reused image.
"""
import time
import random
import urllib.parse
from pathlib import Path

import requests

import config

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}"

# Tune these if you still see 429s, or loosen them once it's reliable.
DELAY_BETWEEN_REQUESTS = 4.0     # seconds, baseline pause between every image call
MAX_RETRIES = 4                  # attempts per scene before giving up on it
BACKOFF_BASE = 6.0               # seconds, grows with each retry (6, 12, 24, 48...)


def _generate_one(prompt: str, width: int, height: int, out_path: Path, timeout: int = 90) -> Path:
    full_prompt = f"{prompt}, {config.IMAGE_STYLE_SUFFIX}"
    encoded = urllib.parse.quote(full_prompt)
    url = POLLINATIONS_URL.format(prompt=encoded)
    params = {"width": width, "height": height, "nologo": "true"}

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, params=params, timeout=timeout)
            if resp.status_code == 429:
                wait = BACKOFF_BASE * (2 ** (attempt - 1)) + random.uniform(0, 2)
                print(f"    [429] rate limited, attempt {attempt}/{MAX_RETRIES}, "
                      f"waiting {wait:.1f}s before retry...")
                time.sleep(wait)
                continue

            resp.raise_for_status()
            out_path.write_bytes(resp.content)

            if out_path.stat().st_size < 1000:
                raise RuntimeError("response too small, likely an error page not an image")

            return out_path

        except requests.exceptions.HTTPError as e:
            last_error = e
            if getattr(e.response, "status_code", None) == 429:
                wait = BACKOFF_BASE * (2 ** (attempt - 1)) + random.uniform(0, 2)
                print(f"    [429 via exception] attempt {attempt}/{MAX_RETRIES}, waiting {wait:.1f}s...")
                time.sleep(wait)
                continue
            raise
        except Exception as e:
            last_error = e
            wait = BACKOFF_BASE * (2 ** (attempt - 1)) + random.uniform(0, 2)
            print(f"    [WARN] attempt {attempt}/{MAX_RETRIES} failed ({e}), waiting {wait:.1f}s...")
            time.sleep(wait)

    raise RuntimeError(f"Failed after {MAX_RETRIES} attempts for prompt '{prompt[:60]}...': {last_error}")


def generate_images_for_scenes(scenes: list[str], story_id: str, width: int, height: int,
                                max_workers: int = 1) -> list[Path]:
    """scenes: list of short text snippets, one per image. Returns image paths
    in the same order as the input scenes (order matters — it's the video's
    scene sequence). max_workers is accepted for backward compatibility but
    ignored — requests are always sequential now, since parallel requests
    are what caused the near-total rate-limit failures."""
    story_dir = config.IMAGE_DIR / story_id
    story_dir.mkdir(parents=True, exist_ok=True)

    results: list[Path] = []
    errors: list[str] = []

    for idx, scene_text in enumerate(scenes):
        out_path = story_dir / f"scene_{idx:03d}.jpg"
        print(f"  Generating image {idx + 1}/{len(scenes)}...")
        try:
            path = _generate_one(scene_text, width, height, out_path)
            results.append(path)
        except Exception as e:
            errors.append(str(e))
            print(f"  [WARN] Giving up on scene {idx + 1}: {e}")

        # pause between every request regardless of success/failure, to stay
        # under the rate limit for the *next* call
        if idx < len(scenes) - 1:
            time.sleep(DELAY_BETWEEN_REQUESTS)

    if not results:
        raise RuntimeError("All image generations failed:\n" + "\n".join(errors))

    if errors:
        print(f"[WARN] {len(errors)}/{len(scenes)} scenes failed to generate an image "
              f"and were skipped. Video will have fewer distinct images than scenes.")

    return results


if __name__ == "__main__":
    test_scenes = [
        "a dark hallway with glowing red eyes staring from the shadows",
        "an old house at night with one lit window",
    ]
    paths = generate_images_for_scenes(test_scenes, "test_story", width=1080, height=1920)
    print(f"[OK] Generated {len(paths)} images:")
    for p in paths:
        print(" -", p)
