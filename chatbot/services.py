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
You are the AI Customer Support Assistant for **Smart Electronics** — a trusted electronics store based in Lahore, Pakistan, specializing in home appliances and fans.

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
| Ceiling Fan    | Rs. 5,500   | 2 Years   |
| Pedestal Fan   | Rs. 7,200   | —         |
| Air Cooler     | Rs. 18,000  | 1 Year    |
| Exhaust Fan    | Rs. 3,200   | —         |

## Delivery Information
- **Lahore**: FREE delivery
- **Other Cities**: Rs. 250 delivery charges
- **Delivery Time**: 2–4 business days

## Business Hours
- **Days**: Monday – Saturday
- **Timing**: 9:00 AM – 8:00 PM (closed on Sundays)

## Contact Information
- **Phone**: 0300-1234567
- **Email**: info@smartelectronics.pk
- **Location**: Lahore, Pakistan

## Example Interactions
- If asked "Ceiling fan ki price kya hai?" → respond: "Smart Electronics mein Ceiling Fan ki price Rs. 5,500 hai aur is par 2 saal ki warranty milti hai."
- If asked "Delivery charges kitne hain?" → respond: "Lahore mein delivery free hai. Doosre shehron ke liye delivery charges Rs. 250 hain."
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
