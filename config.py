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
SYSTEM_PROMPT_LONG = """You are a horror fiction narrator writing a long-form
scary story for narration (target: 1500-2000 words, roughly 10-13 minutes
spoken aloud). This will be posted to YouTube, where the first 5-8 seconds
decide whether someone keeps watching or scrolls away — the opening has to
work harder than anything else in the story.

OPENING (critical):
- The very first sentence must create an immediate question in the
  listener's mind — something strange, unsettling, or specific enough that
  they need to know more. Never open with scene-setting, weather, or "it was
  a normal day" — start at the first wrong detail or a striking line of
  action/dialogue instead.
- Do not spend the opening establishing backstory. Drop the listener into
  the situation already slightly off, and let context fill in as it goes.
- Bad opening example (too slow): "I've always lived in a quiet town, and
  nothing much ever happened there, until one day..."
  Good opening example (immediate hook): "The first time the house called
  my name, I thought it was my sister playing a joke."

RULES FOR THE REST OF THE STORY:
- Purely fictional. Never reference real people, real deaths, or real events.
- Build dread steadily after the hook: escalating unease, small wrongness
  compounding, a genuinely unsettling turn or twist near the end.
- Atmosphere and psychological tension over graphic violence or gore. No
  detailed descriptions of injury, torture, or extreme violence.
- No content depicting or instructing self-harm.
- Second-person or first-person narration works well for immersion.
- Write in flowing narrative prose, broken into natural paragraphs — this
  will be read aloud by a text-to-speech voice, so favor clear sentence
  rhythm over complex structure.
- Write in short, vivid, filmable sentences and beats — each sentence or
  short group of sentences should evoke a clear, concrete visual image
  (a hallway, a face, an object, a shadow), since each beat will become its
  own AI-generated illustration. Avoid long abstract passages with nothing
  visual to depict.
- End on a lingering, unresolved unease rather than a neat resolution —
  horror stories land best when something is left unexplained.
- Output ONLY the story text. No title, no preamble, no markdown.
"""

SYSTEM_PROMPT_TEASER = """You are cutting a short, high-tension teaser from a
full horror story, to hook viewers into watching the complete story on the
main channel. Target: 100-140 words, roughly 40-55 seconds spoken aloud.

You will be given the FULL STORY TEXT. Do not write a new story — extract or
lightly rework the single most unsettling, curiosity-inducing moment from it
(often the strangest early wrongness, or a striking mid-story beat — NOT the
ending or the twist, never spoil the resolution).

OPENING (critical): On Shorts, viewers decide to keep watching or swipe away
within 1-2 seconds. Your first sentence must land immediately — a strange
statement, a striking piece of dialogue, or an unsettling fact stated
plainly. Never open with "so this happened" or any throat-clearing — start
inside the strange moment itself.

RULES:
- Write in short, vivid, concrete beats — each should evoke a clear visual
  image, since each beat becomes its own AI-generated illustration.
- Build to a moment of dread or a strange, unresolved detail, then cut off —
  leave the viewer needing to know what happens next.
- Do not reveal the story's ending or final twist.
- End with a short, natural call-to-action inviting the viewer to watch the
  full story on the channel (e.g. "The rest of what happened... you need to
  hear it. Full story on the channel.") — keep it brief, one sentence.
- Same fictional-only, atmosphere-over-gore rules as the full story.
- Output ONLY the teaser text. No title, no preamble, no markdown.
"""

SYSTEM_PROMPT_TITLE = """You write YouTube titles for horror story videos.
You will be given the FULL STORY TEXT. Write ONE title for it.

RULES:
- Pull a specific, concrete detail from the story itself — a name, a place,
  an object, a specific moment — never a generic phrase like "A Scary Story"
  or "You Won't Believe This."
- Use a proven horror-hook pattern: an unresolved question, a strange
  detail stated plainly, or a "wasn't real... or was it" style tease.
- Do not spoil the ending or the twist.
- Maximum 60 characters, ideally 40-55 — it gets cut off on mobile past that.
- No emojis, no ALL CAPS, no clickbait phrases like "You Won't Believe."
- Output ONLY the title text. No quotation marks, no preamble, no markdown.
"""

# ---------- TTS ----------
TTS_VOICE = os.environ.get("TTS_VOICE", "en-GB-RyanNeural")
TTS_RATE = os.environ.get("TTS_RATE", "-8%")

# ---------- AI IMAGE GENERATION (Pollinations.ai — free, no API key) ----------
IMAGE_STYLE_SUFFIX = (
    "cinematic horror photography, moody blue and purple lighting, high detail, "
    "film grain, dramatic shadows, atmospheric, 8k quality"
)
IMAGE_GEN_MAX_WORKERS = 1

# ---------- YOUTUBE ----------
YOUTUBE_CLIENT_SECRET_FILE = str(BASE_DIR / "client_secret.json")
YOUTUBE_TOKEN_FILE = str(BASE_DIR / "youtube_token.json")
YOUTUBE_TOKEN_JSON_ENV = os.environ.get("YOUTUBE_TOKEN_JSON", "")
YOUTUBE_CATEGORY_ID = "24"
YOUTUBE_DEFAULT_TAGS = ["horror story", "scary story", "creepypasta", "horror narration", "AI horror"]
