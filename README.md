# 🤖 AI Customer Support Chatbot — Smart Electronics

A modern, fully responsive AI-powered customer support chatbot built for **Smart Electronics** (a demo electronics store in Lahore) using **Django** and **Google Gemini API**. Designed as a floating website widget with a premium, professional UI.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-green?logo=django&logoColor=white)
![Gemini](https://img.shields.io/badge/Google_Gemini-API-orange?logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)


---

## ✨ Features

- **Google Gemini AI** — Powered by `gemini-2.0-flash` with automatic model fallback
- **Floating Chat Widget** — Bottom-right launcher icon that opens a sleek chat window
- **Smooth Animations** — Spring-style open/close transitions for the chat widget
- **Responsive Design** — Full-screen on mobile (≤600px), floating card on desktop (440×640px)
- **Copy to Clipboard** — Hover over any message to reveal a copy icon (icon-only, no text)
- **Quick Suggestions** — Horizontal scrollable suggestion chips (Delivery Info, Order Tracking, Payment Options)
- **Menu Drawer** — Hamburger menu (☰) with options for New Conversation, Recent Chats, and Clear History
- **Conversation History** — Chat context is maintained per session for coherent multi-turn dialogue
- **Strictly English** — All AI responses are in fluent, professional English regardless of input language

---

## 🏗️ Architecture

```
User clicks chat icon
    → Chat widget opens (animated)
        → User types message
            → JS fetch() POST /api/chat/
                → Django view → Gemini API
                    → AI reply → Chat window
```

---

## 📁 Project Structure

```
ai_chatbot_mvp/
├── manage.py                        # Django management script
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variable template
├── .gitignore
├── db.sqlite3                       # SQLite database
│
├── chatbot_project/                 # Django project configuration
│   ├── settings.py                  # Settings (static files, apps, middleware)
│   ├── urls.py                      # Root URL config (/ and /api/)
│   └── wsgi.py
│
└── chatbot/                         # Main chatbot application
    ├── views.py                     # chat_page (renders UI) + chat_api (POST endpoint)
    ├── services.py                  # Gemini API integration + system prompt
    ├── urls.py                      # App-level URL patterns (/api/chat/)
    ├── apps.py
    │
    ├── templates/
    │   └── chatbot/
    │       └── chat.html            # Main HTML template ({% load static %})
    │
    └── static/
        ├── chatbot/
        │   ├── css/
        │   │   └── style.css        # Primary stylesheet (widget, responsive, animations)
        │   └── js/
        │       └── main.js          # Primary JS (widget logic, API calls, copy, menu)
        ├── css/
        │   └── chat.css             # Fallback/legacy stylesheet
        └── js/
            └── chat.js              # Fallback/legacy script
```

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.10+
- A [Google Gemini API Key](https://aistudio.google.com/app/apikey)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai_chatbot_mvp.git
cd ai_chatbot_mvp
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Activate:
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DJANGO_SECRET_KEY=your-random-secret-key
DEBUG=True
```

### 5. Run migrations & start the server

```bash
python manage.py migrate
python manage.py runserver
```

### 6. Open in browser

Navigate to **http://127.0.0.1:8000/** — click the chat icon in the bottom-right corner to start chatting!

---

## 🔌 API Reference

### `POST /api/chat/`

Send a user message with optional conversation history.

**Request Body:**

```json
{
  "message": "What are the delivery charges?",
  "history": [
    { "role": "user", "content": "Hello" },
    { "role": "assistant", "content": "Hi there! How can I help you today?" }
  ]
}
```

**Success Response** `200 OK`:

```json
{
  "reply": "Our standard delivery charges vary depending on your location. Could you please share your city so I can provide accurate details?"
}
```

**Error Responses:**

| Status | Body | Cause |
|--------|------|-------|
| `400` | `{"error": "Invalid JSON payload."}` | Malformed JSON in request body |
| `400` | `{"error": "Message field is required."}` | Empty or missing `message` field |

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Django 5.0, Django REST Framework |
| **AI Model** | Google Gemini API (`gemini-2.0-flash`) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Icons** | Font Awesome 6 |
| **Database** | SQLite (default) |
| **Environment** | python-dotenv |
| **CORS** | django-cors-headers |

---

## 🎨 UI Highlights

| Feature | Description |
|---------|-------------|
| **Color Palette** | Clean white/light theme — `#ffffff` widget, `#f8fafc` background, `#4f46e5` accent |
| **Chat Launcher** | Floating indigo icon, hides completely when chat is open |
| **Animations** | Spring-style open/close with CSS keyframes |
| **Mobile** | Full-screen takeover on screens ≤600px |
| **Desktop** | 440px × 640px floating card in bottom-right |
| **Copy Button** | Icon-only on hover (Font Awesome clipboard icon) |
| **Menu** | Slide-down drawer with New Conversation, Recent Chats, Clear History |

---

## 🗺️ Roadmap

- [ ] **Business Context Injection** — Load company info (prices, policies, contact) into the system prompt via Django admin panel
- [ ] **RAG (Retrieval-Augmented Generation)** — Upload PDFs/catalogs, chunk & embed with LangChain, store vectors in ChromaDB/FAISS
- [ ] **WhatsApp Integration** — Connect via Twilio API for omnichannel support
- [ ] **Human Escalation** — "Talk to a human" button for low-confidence answers
- [ ] **User Authentication** — Session-based chat history persistence
- [ ] **Analytics Dashboard** — Track common queries, response times, and satisfaction

---

## 📝 Notes

- **CSRF** is exempted on `/api/chat/` since it's a public-facing API called via JS `fetch()` with no session/auth. Revisit this if you add user authentication.
- **Model Fallback**: The service layer tries models in order: `gemini-2.0-flash` → `gemini-flash-latest` → `gemini-2.5-flash`. If one is unavailable, it automatically falls through to the next.
- **Clipboard API** requires a secure context (HTTPS or localhost). A `document.execCommand('copy')` fallback is included for non-secure environments.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).