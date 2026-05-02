"""
llm.py
------
Provider-agnostic LLM wrapper.

Set LLM_PROVIDER in .env to switch between providers:
  anthropic  (default) — requires ANTHROPIC_API_KEY
  openai               — requires OPENAI_API_KEY
  gemini               — requires GOOGLE_API_KEY

Set LLM_MODEL to override the default model for the chosen provider.
"""

import os
from dotenv import load_dotenv

load_dotenv()

_DEFAULTS = {
    "anthropic": "claude-3-5-sonnet-20241022",
    "openai": "gpt-4o",
    "gemini": "gemini-2.5-flash",
}


def _resolve_provider() -> str:
    explicit = os.getenv("LLM_PROVIDER", "").lower()
    if explicit:
        return explicit
    if os.getenv("GOOGLE_API_KEY"):
        return "gemini"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    return "anthropic"


def generate(prompt: str, system: str = "") -> str:
    """
    Send a prompt to the configured LLM provider and return the response text.

    Args:
        prompt: The user message / query with context.
        system: Optional system prompt.

    Returns:
        The model's response as a plain string.
    """
    provider = _resolve_provider()
    model = os.getenv("LLM_MODEL", "") or _DEFAULTS.get(provider, "")

    if provider == "anthropic":
        return _anthropic(prompt, system, model)
    elif provider == "openai":
        return _openai(prompt, system, model)
    elif provider == "gemini":
        return _gemini(prompt, system, model)
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{provider}'. Choose from: anthropic, openai, gemini."
        )


def _anthropic(prompt: str, system: str, model: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    kwargs = {
        "model": model,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system
    message = client.messages.create(**kwargs)
    return message.content[0].text


def _openai(prompt: str, system: str, model: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model=model,
        max_tokens=1024,
        messages=messages,
    )
    return response.choices[0].message.content


def _gemini(prompt: str, system: str, model: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    full_prompt = f"{system}\n\n{prompt}" if system else prompt
    gemini_model = genai.GenerativeModel(model)
    response = gemini_model.generate_content(full_prompt)
    return response.text
