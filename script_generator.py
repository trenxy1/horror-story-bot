"""
Step 2: Generate a horror story (long or short) from a theme premise, using
Gemini as primary and Groq as automatic fallback if Gemini fails.
"""
import requests

import config


def _call_gemini(system_prompt: str, user_prompt: str, timeout: int, max_tokens: int) -> str:
    if not config.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set")

    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"parts": [{"text": user_prompt}]}],
        "generationConfig": {"temperature": 0.9, "maxOutputTokens": max_tokens},
    }
    resp = requests.post(
        f"{config.GEMINI_URL}?key={config.GEMINI_API_KEY}", json=payload, timeout=timeout
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Gemini API error {resp.status_code}: {resp.text[:300]}")
    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected Gemini response shape: {data}") from e


def _call_groq(system_prompt: str, user_prompt: str, timeout: int, max_tokens: int) -> str:
    if not config.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not set")

    payload = {
        "model": config.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.9,
        "max_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {config.GROQ_API_KEY}", "Content-Type": "application/json"}
    resp = requests.post(config.GROQ_URL, headers=headers, json=payload, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"Groq API error {resp.status_code}: {resp.text[:300]}")
    return resp.json()["choices"][0]["message"]["content"].strip()


def _generate(system_prompt: str, theme: str, max_tokens: int, timeout: int = 90) -> str:
    user_prompt = f"Write the story now. Premise: {theme}"
    providers = [_call_gemini, _call_groq] if config.LLM_PROVIDER == "gemini" else [_call_groq, _call_gemini]

    errors = []
    for fn in providers:
        try:
            result = fn(system_prompt, user_prompt, timeout, max_tokens)
            if result:
                return result
        except Exception as e:
            errors.append(f"{fn.__name__}: {e}")
            print(f"[WARN] {fn.__name__} failed, trying next provider: {e}")

    raise RuntimeError(f"All LLM providers failed for theme '{theme}':\n" + "\n".join(errors))


def generate_long_story(theme: str) -> str:
    return _generate(config.SYSTEM_PROMPT_LONG, theme, max_tokens=3000, timeout=120)


def generate_teaser(full_story_text: str) -> str:
    user_prompt = f"FULL STORY TEXT:\n\n{full_story_text}\n\nWrite the teaser now."
    providers = [_call_gemini, _call_groq] if config.LLM_PROVIDER == "gemini" else [_call_groq, _call_gemini]

    errors = []
    for fn in providers:
        try:
            result = fn(config.SYSTEM_PROMPT_TEASER, user_prompt, timeout=60, max_tokens=400)
            if result:
                return result
        except Exception as e:
            errors.append(f"{fn.__name__}: {e}")
            print(f"[WARN] {fn.__name__} failed, trying next provider: {e}")

    raise RuntimeError("All LLM providers failed generating teaser:\n" + "\n".join(errors))


if __name__ == "__main__":
    import theme_bank
    picked = theme_bank.get_next_theme()
    print(f"Theme: {picked['theme']}\n")
    story = generate_long_story(picked["theme"])
    print("=== LONG STORY ===")
    print(story)
    print("\n=== TEASER ===")
    print(generate_teaser(story))
