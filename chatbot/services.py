"""
Core chatbot logic: builds the prompt and calls the Gemini API.

This version strictly uses Google Gemini API.
"""

import os

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


SYSTEM_PROMPT = """
You are AI Support Assistant, a smart, polite, concise, and highly professional virtual customer support agent.
Always respond strictly in fluent English, regardless of the language used by the user.
Keep your answers clear, helpful, and well-structured using bullet points or paragraphs when appropriate.
If a question requires internal account or private business details that you cannot access, politely inform the user that you will connect them with a human customer support specialist.
"""

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
