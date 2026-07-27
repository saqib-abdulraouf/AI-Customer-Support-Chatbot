"""
Core chatbot logic: builds the prompt and calls the Gemini API.

All company data (name, products, delivery, contact, behavior rules) is
loaded from  company_data.json  — edit that file to change anything.
This file contains only generic logic, zero company-specific text.
"""

import os
import json
from pathlib import Path

# Gemini SDK support
genai = None
genai_client = None

try:
    import google.generativeai as genai
except ImportError:
    try:
        from google import genai as genai_new
        genai_client = genai_new
    except ImportError:
        pass


# ── Load company data from JSON ──────────────────────────────────────
_DATA_FILE = Path(__file__).resolve().parent / "company_data.json"

with open(_DATA_FILE, "r", encoding="utf-8") as _f:
    _COMPANY = json.load(_f)


def _build_system_prompt(data: dict) -> str:
    """Build the full system prompt dynamically from JSON data only."""

    lines = []

    # ── Identity
    lines.append(
        f"You are the AI Customer Support Assistant for "
        f"**{data['company_name']}** — {data['tagline']}"
    )

    # ── Behavior rules
    lines.append("\n## Your Behavior")
    for rule in data.get("bot_behavior", []):
        lines.append(f"- {rule}")

    # ── Product catalog
    lines.append("\n## Product Catalog\n")
    lines.append("| Product | Price (PKR) | Warranty |")
    lines.append("|---------|-------------|----------|")
    for p in data.get("products", []):
        warranty = p["warranty"] if p.get("warranty") else "—"
        lines.append(f"| {p['name']} | {p['price']} | {warranty} |")

    # ── Delivery
    dlv = data.get("delivery", {})
    lines.append("\n## Delivery Information")
    for key, val in dlv.items():
        label = key.replace("_", " ").title()
        lines.append(f"- **{label}**: {val}")

    # ── Business hours
    hrs = data.get("business_hours", {})
    lines.append("\n## Business Hours")
    for key, val in hrs.items():
        label = key.replace("_", " ").title()
        lines.append(f"- **{label}**: {val}")

    # ── Contact
    cnt = data.get("contact", {})
    lines.append("\n## Contact Information")
    for key, val in cnt.items():
        label = key.replace("_", " ").title()
        lines.append(f"- **{label}**: {val}")

    return "\n".join(lines)


SYSTEM_PROMPT = _build_system_prompt(_COMPANY)

# Recommended model sequence for Gemini API
MODEL_CANDIDATES = ["gemini-2.0-flash", "gemini-flash-latest", "gemini-2.5-flash"]


def get_bot_reply(user_message: str, conversation_history: list | None = None) -> str:
    """
    Sends the user's message (plus optional prior turns) to Gemini LLM and returns the assistant's reply.

    conversation_history: list of {"role": "user"/"assistant", "content": str}
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "GEMINI_API_KEY missing. Please set GEMINI_API_KEY in your .env file."

    prompt_parts = [SYSTEM_PROMPT]
    if conversation_history:
        for turn in conversation_history:
            role = turn.get("role")
            content = turn.get("content", "")
            prefix = "User:" if role == "user" else "Assistant:"
            prompt_parts.append(f"{prefix} {content}")
    prompt_parts.append(f"User: {user_message}")
    full_prompt = "\n".join(prompt_parts)

    last_error = None
    for model_name in MODEL_CANDIDATES:
        try:
            if genai and hasattr(genai, "configure"):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(full_prompt)
                return response.text.strip()
            elif genai_client:
                client = genai_client.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=model_name,
                    contents=full_prompt,
                )
                return response.text.strip()
            else:
                return "Google Gemini SDK is not installed. Run `pip install google-generativeai`."
        except Exception as exc:
            last_error = exc
            continue

    return (
        "Sorry, I'm having trouble responding right now. "
        "Please try again in a moment or contact our support team directly. "
        f"(error: {last_error})"
    )
