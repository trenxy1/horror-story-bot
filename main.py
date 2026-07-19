"""
Orchestrator: picks one theme, generates a long story + a teaser cut from it,
generates one AI image per sentence-level scene using REAL word-timestamp
data from the TTS engine, builds both videos, and uploads both.

Usage:
    py main.py                # build both, don't upload
    py main.py --upload       # build both and upload to YouTube (public)
"""
import argparse
import hashlib
import sys
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


def _build_one_video(audio_path, boundaries, story_id: str,
                      tag: str, orientation: str, output_path) -> None:
    total_duration = AudioFileClip(str(audio_path)).duration

    scenes = scene_builder.build_scenes(boundaries, total_audio_duration=total_duration)
    print(f"  {len(scenes)} scenes for {tag} ({total_duration:.0f}s total audio, "
          f"real word-timing aligned)")

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

    print("[1/6] Generating long story...")
    story_text = script_generator.generate_long_story(theme)
    print(f"({len(story_text.split())} words)")

    print("[2/6] Generating teaser cut from that story...")
    teaser_text = script_generator.generate_teaser(story_text)
    print(f"({len(teaser_text.split())} words)")

    print("[3/6] Generating long-story voiceover + word timing...")
    long_audio, long_boundaries = tts_generator.generate_audio_with_timing(story_text, f"{story_id}_long")

    print("[4/6] Generating teaser voiceover + word timing...")
    teaser_audio, teaser_boundaries = tts_generator.generate_audio_with_timing(teaser_text, f"{story_id}_teaser")

    print("[5/6] Generating AI images + building long-form video...")
    long_path = config.VIDEO_DIR / f"{date.today().isoformat()}_{story_id}_long.mp4"
    _build_one_video(long_audio, long_boundaries, story_id, "long", "landscape", long_path)

    print("[6/6] Generating AI images + building teaser video...")
    teaser_path = config.VIDEO_DIR / f"{date.today().isoformat()}_{story_id}_teaser.mp4"
    _build_one_video(teaser_audio, teaser_boundaries, story_id, "teaser", "vertical", teaser_path)

    print(f"[OK] Videos saved: {long_path}, {teaser_path}")
    produced = [str(long_path), str(teaser_path)]

    if do_upload:
        import youtube_upload

        base_title = script_generator.generate_title(story_text)
        print(f"  Generated title: {base_title}")
        
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

    # IMPORTANT: no swallowing here. If the pipeline fails, this function
    # must not return normally with an empty/partial result — that's exactly
    # what caused GitHub to report false "success" on a run that produced
    # nothing. Let the exception propagate; the __main__ guard below turns
    # it into a real non-zero exit code.
    produced = process_story_and_teaser(theme, args.upload)

    print(f"\n=== Done. {len(produced)}/2 videos produced. ===")
    for p in produced:
        print(" -", p)

    if len(produced) < 2:
        raise RuntimeError(f"Only {len(produced)}/2 videos were produced — treating as a failed run.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: Pipeline failed: {e}")
        traceback.print_exc()
        sys.exit(1)
