"""
Splits a story into scenes by SENTENCE (not a fixed word count or time
duration) — each scene is one complete thought/beat, so the AI-generated
image for that scene has a clear, coherent thing to actually depict (a
sentence cut in half produces a muddled, confused image prompt).

Very short sentences get merged with a neighbor so captions don't flicker
too fast; very long sentences get split at a natural point so a single
image isn't stretched across too much text.
"""
import re

MIN_WORDS_PER_SCENE = 5     # merge short sentences until at least this many words
MAX_WORDS_PER_SCENE = 22    # split long sentences beyond this many words


def _split_into_sentences(text: str) -> list[str]:
    text = text.replace("\n", " ").strip()
    raw = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in raw if s.strip()]


def _split_long_sentence(sentence: str, max_words: int) -> list[str]:
    words = sentence.split()
    if len(words) <= max_words:
        return [sentence]
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]


def _merge_short_sentences(sentences: list[str], min_words: int) -> list[str]:
    merged = []
    buffer = ""
    for s in sentences:
        buffer = f"{buffer} {s}".strip() if buffer else s
        if len(buffer.split()) >= min_words:
            merged.append(buffer)
            buffer = ""
    if buffer:
        if merged:
            merged[-1] = f"{merged[-1]} {buffer}".strip()
        else:
            merged.append(buffer)
    return merged


def chunk_into_scene_texts(text: str) -> list[str]:
    sentences = _split_into_sentences(text)

    split_long = []
    for s in sentences:
        split_long.extend(_split_long_sentence(s, MAX_WORDS_PER_SCENE))

    return _merge_short_sentences(split_long, MIN_WORDS_PER_SCENE)


def build_scenes(text: str, total_audio_duration: float) -> list[dict]:
    chunks = chunk_into_scene_texts(text)
    if not chunks:
        return []

    total_words = sum(len(c.split()) for c in chunks) or 1
    scenes = []
    for chunk in chunks:
        share = len(chunk.split()) / total_words
        scenes.append({"text": chunk, "duration": total_audio_duration * share})

    return scenes


if __name__ == "__main__":
    sample = ("The house was quiet. Too quiet. Then the floor creaked upstairs, "
              "even though no one else was home. I called out, but nothing "
              "answered back. Just silence, and then, somehow, closer silence.")
    for s in build_scenes(sample, total_audio_duration=20.0):
        print(f"{s['duration']:.1f}s ({len(s['text'].split())}w): {s['text']}")
