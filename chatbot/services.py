"""
Core chatbot logic: builds the prompt and calls the Gemini API.

Company data is loaded from company_data.json — edit that file to
update products, prices, delivery info, etc. without touching this code.
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
DATA_FILE = Path(__file__).resolve().parent / "company_data.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    COMPANY = json.load(f)


def _build_system_prompt(data: dict) -> str:
    """Build the system prompt dynamically from the company JSON data."""
    company = data["company_name"]
    tagline = data["tagline"]

    # Product catalog table
    product_rows = ""
    for p in data["products"]:
        warranty = p["warranty"] if p["warranty"] else "—"
        product_rows += f"| {p['name']:<14} | {p['price']:<11} | {warranty:<9} |\n"

    # Delivery info
    dlv = data["delivery"]

    # Business hours
    hrs = data["business_hours"]

    # Contact
    cnt = data["contact"]

    return f"""
You are the AI Customer Support Assistant for **{company}** — {tagline}

## Your Behavior
- Always respond strictly in fluent English, regardless of the language used by the user.
- Be smart, polite, concise, and highly professional.
- Keep your answers clear, helpful, and well-structured using bullet points or short paragraphs when appropriate.
- When answering product questions, always mention the price AND any applicable warranty together.
- If a question falls outside the information provided below, politely inform the user that you will connect them with a human support specialist.
- Never make up information that is not listed below.

## Product Catalog

| Product        | Price (PKR) | Warranty  |
|----------------|-------------|-----------|
{product_rows}
## Delivery Information
- **Lahore**: {dlv['lahore']} delivery
- **Other Cities**: {dlv['other_cities']} delivery charges
- **Delivery Time**: {dlv['delivery_time']}

## Business Hours
- **Days**: {hrs['days']}
- **Timing**: {hrs['timing']} (closed on {hrs['closed']})

## Contact Information
- **Phone**: {cnt['phone']}
- **Email**: {cnt['email']}
- **Location**: {cnt['location']}
"""


SYSTEM_PROMPT = _build_system_prompt(COMPANY)

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
