from django.contrib import admin
from django.urls import path, include
from chatbot.views import chat_page

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", chat_page, name="chat_page"),
    path("api/", include("chatbot.urls")),
]
