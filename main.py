"""
Orchestrator: each run picks one horror theme, generates a long narrated
story (uploaded to the main channel) and a separate short scary story
(uploaded as a Short), independent pieces of content, not the same story
cut two ways.

Usage:
    py main.py                # build both, don't upload
    py main.py --upload       # build both and upload to YouTube (public)
"""
import argparse
import hashlib
import traceback
from datetime import date

import config
import theme_bank
import script_generator
import tts_generator
import image_fetch
import video_builder


def _story_id(theme: str, kind: str) -> str:
    return hashlib.sha256(f"{theme}{kind}{date.today().isoformat()}".encode()).hexdigest()[:12]


def process_long_story(theme: str, do_upload: bool) -> str:
    print(f"\n=== LONG STORY | theme: {theme} ===")
    story_id = _story_id(theme, "long")

    print("[1/4] Generating long story...")
    story_text = script_generator.generate_long_story(theme)
    print(f"({len(story_text.split())} words)")

    print("[2/4] Generating voiceover...")
    audio_path = tts_generator.generate_audio(story_text, f"{story_id}_long")

    print("[3/4] Fetching images...")
    images = image_fetch.fetch_images(story_id, count=config.IMAGES_PER_LONG_VIDEO)

    print("[4/4] Building video...")
    out_path = config.VIDEO_DIR / f"{date.today().isoformat()}_{story_id}_long.mp4"
    video_builder.build_video(images, audio_path, story_text, "A True Horror Story",
                               out_path, orientation="landscape")
    print(f"[OK] Video saved: {out_path}")

    if do_upload:
        import youtube_upload
        title = "A Horror Story You Won't Forget"
        description = f"{story_text}\n\n#HorrorStory #ScaryStory #Creepypasta"
        youtube_upload.upload_video(out_path, title, description, privacy="public")

    return str(out_path)


def process_short_story(theme: str, do_upload: bool) -> str:
    print(f"\n=== SHORT STORY | theme: {theme} ===")
    story_id = _story_id(theme, "short")

    print("[1/4] Generating short story...")
    story_text = script_generator.generate_short_story(theme)
    print(f"({len(story_text.split())} words)")

    print("[2/4] Generating voiceover...")
    audio_path = tts_generator.generate_audio(story_text, f"{story_id}_short")

    print("[3/4] Fetching images...")
    images = image_fetch.fetch_images(story_id, count=config.IMAGES_PER_SHORT_VIDEO)

    print("[4/4] Building video...")
    out_path = config.VIDEO_DIR / f"{date.today().isoformat()}_{story_id}_short.mp4"
    video_builder.build_video(images, audio_path, story_text, "Scary Story",
                               out_path, orientation="vertical")
    print(f"[OK] Video saved: {out_path}")

    if do_upload:
        import youtube_upload
        title = "This Will Give You Chills #Shorts"
        description = f"{story_text}\n\n#Shorts #HorrorStory #Creepy"
        youtube_upload.upload_video(out_path, title, description, privacy="public")

    return str(out_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload", action="store_true", help="Upload both videos to YouTube")
    args = parser.parse_args()

    picked = theme_bank.get_next_theme()
    theme = picked["theme"]
    print(f"Selected theme #{picked['index']}: {theme}")

    produced = []
    for fn in (process_long_story, process_short_story):
        try:
            produced.append(fn(theme, args.upload))
        except Exception as e:
            print(f"[ERROR] {fn.__name__} failed: {e}")
            traceback.print_exc()

    print(f"\n=== Done. {len(produced)}/2 videos produced. ===")
    for p in produced:
        print(" -", p)


if __name__ == "__main__":
    main()
  
