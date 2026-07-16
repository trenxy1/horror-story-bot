"""
Step 5: Assemble images + voiceover + captions into a finished MP4.
Supports "landscape" (main channel) and "vertical" (Shorts) orientations.
Caption chunking is word-count based (not a fixed division) so it scales
correctly for both a 60-second short and a 12-minute long-form story.
"""
import textwrap
from pathlib import Path

from moviepy.editor import (
    AudioFileClip, ImageClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, vfx,
)

import config

FPS = 24
FONT = "DejaVu-Sans-Bold"
WORDS_PER_CAPTION = 14   # roughly how many words show on screen at once

ORIENTATIONS = {
    "landscape": {"w": 1920, "h": 1080},
    "vertical": {"w": 1080, "h": 1920},
}


def _cover_scale(clip, target_w, target_h):
    img_w, img_h = clip.size
    return max(target_w / img_w, target_h / img_h)


def _ken_burns_clip(img_path: Path, duration: float, w: int, h: int, zoom_ratio: float = 0.06):
    clip = ImageClip(str(img_path)).set_duration(duration)
    base_scale = _cover_scale(clip, w, h) * 1.1
    clip = clip.fx(vfx.resize, lambda t: base_scale * (1 + zoom_ratio * (t / duration)))
    clip = clip.set_position("center")
    return clip


def _caption_chunks(script_text: str, words_per_chunk: int = WORDS_PER_CAPTION) -> list[str]:
    words = script_text.replace("\n", " ").split()
    return [" ".join(words[i:i + words_per_chunk]) for i in range(0, len(words), words_per_chunk)]


def _wrapped_caption(text: str, duration: float, start: float, w: int, h: int, wrap_width: int):
    wrapped = "\n".join(textwrap.wrap(text, width=wrap_width))
    txt = TextClip(
        wrapped, fontsize=42 if w < h else 46, color="white", font=FONT,
        stroke_color="black", stroke_width=3,
        method="caption", size=(w - 120, None), align="center",
        bg_color="rgba(0,0,0,0.6)",
    )
    bottom_margin = 500 if w < h else 280
    txt = txt.set_position(("center", h - bottom_margin)).set_start(start).set_duration(duration)
    return txt


def build_video(images: list[Path], audio_path: Path, script_text: str,
                 title_card: str, output_path: Path, orientation: str = "landscape") -> Path:
    dims = ORIENTATIONS[orientation]
    w, h = dims["w"], dims["h"]
    wrap_width = 26 if orientation == "vertical" else 36

    audio = AudioFileClip(str(audio_path))
    duration = audio.duration

    if not images:
        raise ValueError("No images provided for video assembly")

    per_image = duration / len(images)
    bg_clips = [_ken_burns_clip(p, per_image, w, h) for p in images]
    background = concatenate_videoclips(bg_clips, method="compose").set_audio(audio)

    title_top = 200 if orientation == "vertical" else None
    title_txt = TextClip(
        title_card, fontsize=50 if orientation == "vertical" else 56, color="white", font=FONT,
        stroke_color="black", stroke_width=4,
        method="caption", size=(w - 160, None), align="center",
        bg_color="rgba(0,0,0,0.55)",
    )
    pos = ("center", title_top) if title_top else "center"
    title_txt = title_txt.set_position(pos).set_start(0).set_duration(min(4, duration))

    chunks = _caption_chunks(script_text)
    caption_clips = []
    if chunks:
        seg = duration / len(chunks)
        for i, chunk in enumerate(chunks):
            caption_clips.append(_wrapped_caption(chunk, seg, i * seg, w, h, wrap_width))

    final = CompositeVideoClip(
        [background, title_txt, *caption_clips], size=(w, h)
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.write_videofile(
        str(output_path), fps=FPS, codec="libx264", audio_codec="aac",
        preset="medium", threads=4,
    )
    return output_path


if __name__ == "__main__":
    print("Run this via main.py — it needs images + an audio file + a script to work with.")
