"""
Assembles scenes (text + matching AI-generated image) into a finished MP4.
Caption style: bold, tight lines, plain stroke outline (no background box) —
closer to the clean reference look than the old boxed-caption style.
"""
import textwrap
from pathlib import Path

from moviepy.editor import (
    AudioFileClip, ImageClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, vfx,
)

import config

FPS = 24
FONT = "DejaVu-Sans-Bold-Oblique"   # bold italic-leaning — closer to the reference style
FONT_FALLBACK = "DejaVu-Sans-Bold"  # used automatically if the oblique variant isn't found

ORIENTATIONS = {
    "landscape": {"w": 1920, "h": 1080},
    "vertical": {"w": 1080, "h": 1920},
}


def _cover_scale(clip, target_w, target_h):
    img_w, img_h = clip.size
    return max(target_w / img_w, target_h / img_h)


def _ken_burns_clip(img_path: Path, duration: float, w: int, h: int, zoom_ratio: float = 0.05):
    clip = ImageClip(str(img_path)).set_duration(duration)
    base_scale = _cover_scale(clip, w, h) * 1.08
    clip = clip.fx(vfx.resize, lambda t: base_scale * (1 + zoom_ratio * (t / duration)))
    clip = clip.set_position("center")
    return clip


def _make_text_clip(text: str, fontsize: int, w: int, wrap_width: int, stroke_width: int):
    wrapped = "\n".join(textwrap.wrap(text, width=wrap_width))
    try:
        return TextClip(
            wrapped, fontsize=fontsize, color="white", font=FONT,
            stroke_color="black", stroke_width=stroke_width,
            method="caption", size=(w - 100, None), align="center",
        )
    except Exception:
        return TextClip(
            wrapped, fontsize=fontsize, color="white", font=FONT_FALLBACK,
            stroke_color="black", stroke_width=stroke_width,
            method="caption", size=(w - 100, None), align="center",
        )


def build_video_from_scenes(scenes: list[dict], audio_path: Path, output_path: Path,
                             orientation: str = "landscape") -> Path:
    """scenes: list of {"text": str, "image": Path, "duration": float}
    Each scene gets its own Ken Burns image clip and its own caption, timed
    to exactly match that portion of the audio."""
    dims = ORIENTATIONS[orientation]
    w, h = dims["w"], dims["h"]
    wrap_width = 22 if orientation == "vertical" else 32
    fontsize = 54 if orientation == "vertical" else 58

    audio = AudioFileClip(str(audio_path))

    bg_clips = []
    caption_clips = []
    t_cursor = 0.0
    for scene in scenes:
        dur = scene["duration"]
        bg_clips.append(_ken_burns_clip(scene["image"], dur, w, h))

        cap = _make_text_clip(scene["text"], fontsize, w, wrap_width, stroke_width=3)
        bottom_margin = 420 if orientation == "vertical" else 220
        cap = cap.set_position(("center", h - bottom_margin)).set_start(t_cursor).set_duration(dur)
        caption_clips.append(cap)

        t_cursor += dur

    background = concatenate_videoclips(bg_clips, method="compose").set_audio(audio)

    final = CompositeVideoClip([background, *caption_clips], size=(w, h))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.write_videofile(
        str(output_path), fps=FPS, codec="libx264", audio_codec="aac",
        preset="medium", threads=4,
    )
    return output_path


if __name__ == "__main__":
    print("Run this via main.py — needs scenes with matching images + an audio file.")
                                 
