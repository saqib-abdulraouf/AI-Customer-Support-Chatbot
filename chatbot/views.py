import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest

from .models import Company
from .services import get_bot_reply


def chat_page(request):
    """Renders the chat widget frontend page."""
    return render(request, "chat.html")


@csrf_exempt
def chat_api(request):
    """
    POST /api/chat/
    Headers (optional): X-API-Key: key_xxx
    Body: {
      "message": "Ceiling fan ki price kya hai?",
      "history": [...],
      "api_key": "key_xxx",      # optional tenant API key
      "company": "smart-electronics"  # optional tenant slug
    }
    Returns: { "reply": "...", "tenant": "Smart Electronics" }
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    user_message = data.get("message", "").strip()
    history = data.get("history", [])
    if not user_message:
        return JsonResponse({"error": "Message field is required."}, status=400)

    # Multi-tenant authentication (Header or Payload)
    api_key = request.headers.get("X-API-Key") or data.get("api_key")
    company_slug = data.get("company")

    company = None
    if api_key:
        company = Company.objects.filter(api_key=api_key, is_active=True).first()
    elif company_slug:
        company = Company.objects.filter(slug=company_slug, is_active=True).first()

    reply = get_bot_reply(user_message, conversation_history=history, company=company)

    response_data = {"reply": reply}
    if company:
        response_data["tenant"] = company.name

    return JsonResponse(response_data)
