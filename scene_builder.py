"""
Splits a story into scenes (text chunks), each of which will get its own
AI-generated image and its own caption timing. Scene duration is estimated
proportionally by word count against the actual TTS audio duration — simple,
and accurate enough since TTS speaks at a fairly steady pace.
"""
import config


def chunk_into_scenes(text: str, words_per_scene: int) -> list[str]:
    words = text.replace("\n", " ").split()
    return [" ".join(words[i:i + words_per_scene]) for i in range(0, len(words), words_per_scene)]


def build_scenes(text: str, words_per_scene: int, total_audio_duration: float) -> list[dict]:
    """Returns [{"text": str, "duration": float}, ...] — durations sum to
    total_audio_duration, proportioned by each scene's share of total words."""
    chunks = chunk_into_scenes(text, words_per_scene)
    total_words = sum(len(c.split()) for c in chunks) or 1

    scenes = []
    for chunk in chunks:
        share = len(chunk.split()) / total_words
        scenes.append({"text": chunk, "duration": total_audio_duration * share})

    return scenes


if __name__ == "__main__":
    sample = "The house was quiet. Too quiet. Then the floor creaked upstairs, even though no one else was home."
    for s in build_scenes(sample, words_per_scene=8, total_audio_duration=10.0):
        print(s)
