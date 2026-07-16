"""
Step 1: Instead of fetching real headlines, this rotates through a bank of
horror story premises so successive runs don't repeat themselves too soon.
"""
import json
import random
from datetime import datetime, timezone

import config


def load_state() -> dict:
    if config.THEMES_FILE.exists():
        with open(config.THEMES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"used_indices": []}


def save_state(state: dict):
    with open(config.THEMES_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def get_next_theme() -> dict:
    """Returns {'theme': str, 'index': int}. Cycles through THEME_BANK,
    resetting once every theme has been used at least once."""
    state = load_state()
    used = set(state.get("used_indices", []))
    all_indices = set(range(len(config.THEME_BANK)))

    available = list(all_indices - used)
    if not available:
        # full cycle complete — reset and start again
        available = list(all_indices)
        used = set()

    idx = random.choice(available)
    used.add(idx)

    state["used_indices"] = list(used)
    state["last_picked_at"] = datetime.now(timezone.utc).isoformat()
    save_state(state)

    return {"theme": config.THEME_BANK[idx], "index": idx}


if __name__ == "__main__":
    picked = get_next_theme()
    print(f"[OK] Picked theme #{picked['index']}: {picked['theme']}")
