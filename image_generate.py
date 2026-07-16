"""
Generates AI images tied directly to each scene of the story, using
Pollinations.ai — a free, no-signup, no-API-key image generation service.
Each image's prompt is built from that scene's actual text plus a fixed
style suffix, so every image in a video shares a consistent moody look
AND actually depicts that moment of the story (not generic stock photos).
"""
import urllib.parse
import concurrent.futures
from pathlib import Path

import requests

import config

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}"


def _generate_one(prompt: str, width: int, height: int, out_path: Path, timeout: int = 90) -> Path:
    full_prompt = f"{prompt}, {config.IMAGE_STYLE_SUFFIX}"
    encoded = urllib.parse.quote(full_prompt)
    url = POLLINATIONS_URL.format(prompt=encoded)
    params = {"width": width, "height": height, "nologo": "true"}

    resp = requests.get(url, params=params, timeout=timeout)
    resp.raise_for_status()
    out_path.write_bytes(resp.content)
    if out_path.stat().st_size < 1000:
        raise RuntimeError(f"Image generation returned suspiciously small file for prompt: {prompt[:60]}")
    return out_path


def generate_images_for_scenes(scenes: list[str], story_id: str, width: int, height: int,
                                max_workers: int = 4) -> list[Path]:
    """scenes: list of short text snippets, one per image. Returns image paths
    in the same order as the input scenes (order matters — it's the video's
    scene sequence)."""
    story_dir = config.IMAGE_DIR / story_id
    story_dir.mkdir(parents=True, exist_ok=True)

    results: dict[int, Path] = {}
    errors: list[str] = []

    def _task(idx_scene):
        idx, scene_text = idx_scene
        out_path = story_dir / f"scene_{idx:03d}.jpg"
        return idx, _generate_one(scene_text, width, height, out_path)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_task, item) for item in enumerate(scenes)]
        for future in concurrent.futures.as_completed(futures):
            try:
                idx, path = future.result()
                results[idx] = path
            except Exception as e:
                errors.append(str(e))
                print(f"[WARN] Image generation failed for one scene: {e}")

    if not results:
        raise RuntimeError("All image generations failed:\n" + "\n".join(errors))

    # return in original scene order, skipping any that failed
    return [results[i] for i in sorted(results.keys())]


if __name__ == "__main__":
    test_scenes = [
        "a dark hallway with glowing red eyes staring from the shadows",
        "an old house at night with one lit window",
    ]
    paths = generate_images_for_scenes(test_scenes, "test_story", width=1080, height=1920)
    print(f"[OK] Generated {len(paths)} images:")
    for p in paths:
        print(" -", p)
        
