"""LLM API clients · Gemini (free) + Claude (paid)"""

import base64
import requests

GEMINI_MODELS = {
    "gemini-2.5-flash": "🚀 Gemini 2.5 Flash (ล่าสุด)",
    "gemini-2.0-flash": "⚡ Gemini 2.0 Flash (เสถียร)",
    "gemini-1.5-flash": "📦 Gemini 1.5 Flash (backup)",
}
CLAUDE_MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 8000


def call_gemini(api_key: str, system: str, user_prompt: str,
                image_bytes: bytes | None = None,
                model: str = "gemini-2.5-flash") -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    combined = f"{system}\n\n---\n\n{user_prompt}"
    parts = [{"text": combined}]
    if image_bytes:
        parts.insert(0, {
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_bytes).decode("utf-8"),
            }
        })
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"maxOutputTokens": MAX_TOKENS, "temperature": 0.3},
    }
    r = requests.post(url, json=payload, timeout=180)
    r.raise_for_status()
    data = r.json()
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError(f"No response from Gemini: {data}")
    return candidates[0]["content"]["parts"][0]["text"]


def call_claude(api_key: str, system: str, user_prompt: str,
                image_bytes: bytes | None = None) -> str:
    try:
        import anthropic
    except ImportError as e:
        raise RuntimeError("anthropic package not installed") from e
    client = anthropic.Anthropic(api_key=api_key)
    content: list = [{"type": "text", "text": user_prompt}]
    if image_bytes:
        content.insert(0, {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": base64.b64encode(image_bytes).decode("utf-8"),
            },
        })
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": content}],
    )
    return response.content[0].text
