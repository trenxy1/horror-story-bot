"""
Step 3: Convert a story script to an MP3 voiceover using edge-tts, with a
slightly slowed rate for a more ominous narration feel.
"""
import asyncio
from pathlib import Path

import edge_tts

import config


async def _generate(text: str, out_path: Path, voice: str, rate: str):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(str(out_path))


def generate_audio(script_text: str, filename: str, voice: str | None = None,
                    rate: str | None = None) -> Path:
    voice = voice or config.TTS_VOICE
    rate = rate or config.TTS_RATE
    out_path = config.AUDIO_DIR / f"{filename}.mp3"
    asyncio.run(_generate(script_text, out_path, voice, rate))
    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RuntimeError(f"TTS failed to produce audio at {out_path}")
    return out_path


if __name__ == "__main__":
    test_script = "The house was quiet. Too quiet. And then, from upstairs, a floorboard creaked."
    path = generate_audio(test_script, "test_voice")
    print(f"[OK] Saved audio to {path}")
