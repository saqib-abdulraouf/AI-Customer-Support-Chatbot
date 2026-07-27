"""
Core chatbot logic: builds the prompt and calls the Gemini API.

All knowledge is auto-loaded from the  knowledge/  folder.
Drop any .json file in that folder and restart the server —
the bot will automatically know about it. Zero code changes needed.
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


# ── Auto-load JSON files from knowledge/ folder ──────────────────────
_KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"


def _load_all_knowledge(company_slug: str | None = None) -> dict:
    """Scan knowledge/ folder (or knowledge/<company_slug>/ if present) and load .json files."""
    knowledge = {}
    target_dir = _KNOWLEDGE_DIR

    if company_slug and (_KNOWLEDGE_DIR / company_slug).is_dir():
        target_dir = _KNOWLEDGE_DIR / company_slug

    if not target_dir.exists():
        return knowledge

    for json_file in sorted(target_dir.glob("*.json")):
        with open(json_file, "r", encoding="utf-8") as f:
            knowledge[json_file.stem] = json.load(f)

    # Fallback to root company.json if tenant subfolder doesn't have company.json
    if "company" not in knowledge and (_KNOWLEDGE_DIR / "company.json").exists():
        with open(_KNOWLEDGE_DIR / "company.json", "r", encoding="utf-8") as f:
            knowledge["company"] = json.load(f)

    return knowledge


def _json_to_readable(data, indent=0) -> str:
    """Recursively convert any JSON structure into clean readable text."""
    lines = []
    prefix = "  " * indent

    if isinstance(data, dict):
        for key, val in data.items():
            label = key.replace("_", " ").title()
            if isinstance(val, (dict, list)):
                lines.append(f"{prefix}**{label}**:")
                lines.append(_json_to_readable(val, indent + 1))
            else:
                display = val if val is not None else "—"
                lines.append(f"{prefix}- **{label}**: {display}")

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                parts = []
                for k, v in item.items():
                    label = k.replace("_", " ").title()
                    display = v if v is not None else "—"
                    parts.append(f"{label}: {display}")
                lines.append(f"{prefix}- {' | '.join(parts)}")
            else:
                lines.append(f"{prefix}- {item}")
    else:
        lines.append(f"{prefix}{data}")

    return "\n".join(lines)


def _build_system_prompt(knowledge: dict, company_obj=None) -> str:
    """Build the full system prompt from all loaded knowledge files."""
    lines = []

    # ── Identity (from company.json or Company model)
    company_data = knowledge.get("company", {})
    name = company_obj.name if company_obj else company_data.get("company_name", "Our Company")
    tagline = company_data.get("tagline", "")
    lines.append(f"You are the AI Customer Support Assistant for **{name}** — {tagline}")

    # ── Behavior rules
    rules = company_data.get("bot_behavior", [])
    if rules:
        lines.append("\n## Your Behavior")
        for rule in rules:
            lines.append(f"- {rule}")

    # ── All other knowledge files
    for filename, data in knowledge.items():
        if filename == "company":
            extras = {k: v for k, v in data.items()
                      if k not in ("company_name", "tagline", "bot_behavior")}
            if extras:
                lines.append("\n## Company Details")
                lines.append(_json_to_readable(extras))
            continue

        section_title = filename.replace("_", " ").title()
        lines.append(f"\n## {section_title}")
        lines.append(_json_to_readable(data))

    return "\n".join(lines)


from .rag_service import search_similar_chunks

_DEFAULT_KNOWLEDGE = _load_all_knowledge()
DEFAULT_SYSTEM_PROMPT = _build_system_prompt(_DEFAULT_KNOWLEDGE)

# Recommended model sequence for Gemini API
MODEL_CANDIDATES = ["gemini-2.0-flash", "gemini-flash-latest", "gemini-2.5-flash"]


def get_bot_reply(user_message: str, conversation_history: list | None = None, company=None) -> str:
    """
    Sends user's message to Gemini LLM and returns assistant's reply.

    Integrates Multi-Tenant RAG:
    - Filters ChromaDB vector search by `company_id`
    - Loads per-tenant knowledge JSON files
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "GEMINI_API_KEY missing. Please set GEMINI_API_KEY in your .env file."

    company_id = company.id if company else None
    company_slug = company.slug if company else None

    # Load tenant-specific system prompt if custom company provided
    if company_slug:
        tenant_knowledge = _load_all_knowledge(company_slug=company_slug)
        system_prompt = _build_system_prompt(tenant_knowledge, company_obj=company)
    else:
        system_prompt = DEFAULT_SYSTEM_PROMPT

    # RAG Vector Search: find top 3 relevant chunks from ChromaDB (filtered by tenant company_id)
    rag_chunks = search_similar_chunks(user_message, company_id=company_id, top_k=3)
    dynamic_prompt = system_prompt
    if rag_chunks:
        context_str = "\n\n".join([f"--- Chunk {i+1} ---\n{chunk}" for i, chunk in enumerate(rag_chunks)])
        dynamic_prompt += f"\n\n## Relevant Context from Uploaded Documents (RAG)\n{context_str}\n"

    prompt_parts = [dynamic_prompt]
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
