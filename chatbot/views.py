from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest

from .services import get_bot_reply


def chat_page(request):
    """Renders the simple chat frontend."""
    return render(request, "chatbot/chat.html")


@csrf_exempt
def chat_api(request):
    """
    POST /api/chat/
    body: { "message": "Delivery charges kitne hain?", "history": [...] }
    returns: { "reply": "..." }
    """
    import json
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)
    user_message = data.get("message", "").strip()
    history = data.get("history", [])
    if not user_message:
        return JsonResponse({"error": "Message field is required."}, status=400)
    reply = get_bot_reply(user_message, conversation_history=history)
    return JsonResponse({"reply": reply})
