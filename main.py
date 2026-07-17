"""
Orchestrator: picks one theme, generates a long story + a teaser cut from it,
generates one AI image per SENTENCE-LEVEL scene (so every image matches
exactly what's being said at that moment), builds both videos, and uploads
both (teaser links to the full story).

Usage:
    py main.py                # build both, don't upload
    py main.py --upload       # build both and upload to YouTube (public)
"""
import argparse
import hashlib
import traceback
from datetime import date

from moviepy.editor import AudioFileClip

import config
import theme_bank
import script_generator
import tts_generator
import scene_builder
import image_generate
import video_builder


def _story_id(theme: str) -> str:
    return hashlib.sha256(f"{theme}{date.today().isoformat()}".encode()).hexdigest()[:12]


def _build_one_video(text: str, audio_path, story_id: str,
                      tag: str, orientation: str, output_path) -> None:
    duration = AudioFileClip(str(audio_path)).duration

    scenes = scene_builder.build_scenes(text, duration)
    print(f"  {len(scenes)} scenes for {tag} ({duration:.0f}s total audio, "
          f"~{duration / max(len(scenes), 1):.1f}s/scene average)")

    dims = video_builder.ORIENTATIONS[orientation]
    image_paths = image_generate.generate_images_for_scenes(
        [s["text"] for s in scenes], f"{story_id}_{tag}", dims["w"], dims["h"],
    )

    scenes = scenes[: len(image_paths)]
    for scene, img_path in zip(scenes, image_paths):
        scene["image"] = img_path

    video_builder.build_video_from_scenes(scenes, audio_path, output_path, orientation=orientation)


def process_story_and_teaser(theme: str, do_upload: bool) -> list[str]:
    print(f"\n=== theme: {theme} ===")
    story_id = _story_id(theme)
    produced = []

    print("[1/6] Generating long story...")
    story_text = script_generator.generate_long_story(theme)
    print(f"({len(story_text.split())} words)")

    print("[2/6] Generating teaser cut from that story...")
    teaser_text = script_generator.generate_teaser(story_text)
    print(f"({len(teaser_text.split())} words)")

    print("[3/6] Generating long-story voiceover...")
    long_audio = tts_generator.generate_audio(story_text, f"{story_id}_long")

    print("[4/6] Generating teaser voiceover...")
    teaser_audio = tts_generator.generate_audio(teaser_text, f"{story_id}_teaser")

    print("[5/6] Generating AI images + building long-form video...")
    long_path = config.VIDEO_DIR / f"{date.today().isoformat()}_{story_id}_long.mp4"
    _build_one_video(story_text, long_audio, story_id, "long", "landscape", long_path)

    print("[6/6] Generating AI images + building teaser video...")
    teaser_path = config.VIDEO_DIR / f"{date.today().isoformat()}_{story_id}_teaser.mp4"
    _build_one_video(teaser_text, teaser_audio, story_id, "teaser", "vertical", teaser_path)

    print(f"[OK] Videos saved: {long_path}, {teaser_path}")
    produced = [str(long_path), str(teaser_path)]

    if do_upload:
        import youtube_upload

        base_title = "A Horror Story You Won't Forget"

        long_description = f"{story_text}\n\n#HorrorStory #ScaryStory #Creepypasta"
        long_video_id = youtube_upload.upload_video(
            long_path, base_title, long_description, privacy="public"
        )

        teaser_description = (
            f"{teaser_text}\n\n"
            f"Watch the FULL story here: https://youtu.be/{long_video_id}\n\n"
            f"#Shorts #HorrorStory #Creepy"
        )
        youtube_upload.upload_video(
            teaser_path, f"{base_title} #Shorts", teaser_description, privacy="public"
        )

    return produced


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload", action="store_true", help="Upload both videos to YouTube")
    args = parser.parse_args()

    picked = theme_bank.get_next_theme()
    theme = picked["theme"]
    print(f"Selected theme #{picked['index']}: {theme}")

    try:
        produced = process_story_and_teaser(theme, args.upload)
    except Exception as e:
        print(f"[ERROR] Pipeline failed: {e}")
        traceback.print_exc()
        produced = []

    print(f"\n=== Done. {len(produced)}/2 videos produced. ===")
    for p in produced:
        print(" -", p)


if __name__ == "__main__":
    main()
