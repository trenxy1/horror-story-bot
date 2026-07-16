"""
Config for the AI Horror Storytelling bot.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "output" / "data"
AUDIO_DIR = BASE_DIR / "output" / "audio"
IMAGE_DIR = BASE_DIR / "output" / "images"
VIDEO_DIR = BASE_DIR / "output" / "videos"

for d in (DATA_DIR, AUDIO_DIR, IMAGE_DIR, VIDEO_DIR):
    d.mkdir(parents=True, exist_ok=True)

THEMES_FILE = DATA_DIR / "themes.json"

# ---------- STORY THEMES ----------
# A rotating bank of horror premises. Each run picks the next unused one.
# When all are used, the pool resets (themes can repeat after a full cycle —
# the AI writes a different story from the same premise each time anyway).
THEME_BANK = [
    "a family moves into a house where the previous owners vanished without a trace",
    "a night-shift hospital worker keeps hearing their own name called from empty rooms",
    "a hiker finds a cabin in the woods that shouldn't exist on any map",
    "a child's imaginary friend starts leaving physical evidence of being real",
    "a person receives text messages from a phone number that was disconnected years ago",
    "an antique mirror shows a reflection that moves a half-second too late",
    "a small town's residents all share the exact same recurring nightmare",
    "a delivery driver keeps getting sent to an address that doesn't exist",
    "a family heirloom object seems to follow its owner no matter how many times it's discarded",
    "a group of friends discover an abandoned amusement park still running at night",
    "a person wakes up every day in a slightly different version of their own house",
    "a lighthouse keeper's replacement finds strange marks scratched into every wall",
    "an old radio starts picking up broadcasts from a town that burned down decades ago",
    "a babysitter realizes the house's security cameras show a different time than the clock",
    "a hitchhiker gives directions that lead further into the woods, never out",
    "a photographer notices the same shadowy figure in every photo she's ever taken",
    "residents of an apartment building all report the same knock at 3:17 AM",
    "a fisherman keeps pulling up the same drowned object no matter where he casts",
    "a museum's newest exhibit seems to rearrange itself when no one is looking",
    "a long-abandoned subway station has lights that turn on only for one person",
]

# ---------- LLM PROVIDER ----------
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "gemini")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")

# ---------- SYSTEM PROMPTS ----------
# Both prompts keep content fictional, atmosphere-driven, and free of graphic
# gore, real people, or anything that reads as instructional self-harm/violence
# content — this matters for YouTube monetization/policy, not just taste.

SYSTEM_PROMPT_LONG = """You are a horror fiction narrator writing a long-form
scary story for narration (target: 1500-2000 words, roughly 10-13 minutes
spoken aloud).

RULES:
- Purely fictional. Never reference real people, real deaths, or real events.
- Build dread gradually: ordinary setting, small wrongness, escalating unease,
  a genuinely unsettling turn or twist near the end.
- Atmosphere and psychological tension over graphic violence or gore. No
  detailed descriptions of injury, torture, or extreme violence.
- No content depicting or instructing self-harm.
- Second-person or first-person narration works well for immersion.
- Write in flowing narrative prose, broken into natural paragraphs — this
  will be read aloud by a text-to-speech voice, so favor clear sentence
  rhythm over complex structure.
- End on a lingering, unresolved unease rather than a neat resolution —
  horror stories land best when something is left unexplained.
- Output ONLY the story text. No title, no preamble, no markdown.
"""

SYSTEM_PROMPT_SHORT = """You are a horror fiction narrator writing a very
short scary story for a YouTube Short (target: 120-160 words, roughly 45-60
seconds spoken aloud).

RULES:
- Purely fictional. Never reference real people, real deaths, or real events.
- One unsettling idea, delivered fast: setup, a wrong detail, a gut-punch
  final line. No slow build — this needs to hook in the first sentence.
- Atmosphere and psychological unease over graphic violence or gore.
- No content depicting or instructing self-harm.
- The final sentence should land like a twist or a chill, something that
  makes someone want to see more from the channel.
- Output ONLY the story text. No title, no preamble, no markdown.
"""

# ---------- TTS ----------
# Slightly slower pace reads as more ominous for horror narration.
TTS_VOICE = os.environ.get("TTS_VOICE", "en-GB-RyanNeural")
TTS_RATE = os.environ.get("TTS_RATE", "-8%")

# ---------- IMAGES (Pexels) ----------
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
IMAGE_SEARCH_QUERIES = [
    "foggy forest night",
    "abandoned house dark",
    "empty hallway shadow",
    "old mirror dim light",
    "creepy abandoned building",
    "dark woods path",
    "old house window night",
    "empty room moonlight",
]
IMAGES_PER_LONG_VIDEO = 14   # more images for longer runtime
IMAGES_PER_SHORT_VIDEO = 5

# ---------- YOUTUBE ----------
YOUTUBE_CLIENT_SECRET_FILE = str(BASE_DIR / "client_secret.json")
YOUTUBE_TOKEN_FILE = str(BASE_DIR / "youtube_token.json")
YOUTUBE_TOKEN_JSON_ENV = os.environ.get("YOUTUBE_TOKEN_JSON", "")
YOUTUBE_CATEGORY_ID = "24"  # Entertainment
YOUTUBE_DEFAULT_TAGS = ["horror story", "scary story", "creepypasta", "horror narration", "AI horror"]
