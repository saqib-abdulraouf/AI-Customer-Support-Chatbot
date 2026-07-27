# 🤖 AI Customer Support Chatbot — Smart Electronics

A modern, fully responsive AI-powered customer support chatbot built for **Smart Electronics** (a demo electronics store in Lahore) using **Django** and **Google Gemini API**. Designed as a floating website widget with a premium, professional UI.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-green?logo=django&logoColor=white)
![Gemini](https://img.shields.io/badge/Google_Gemini-API-orange?logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

- **Google Gemini AI** — Powered by `gemini-2.0-flash` with automatic model fallback
- **JSON-Driven Company Data** — All business info (products, prices, delivery, contact) lives in a single `company_data.json` file — no code changes needed to update
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
                → Django view → services.py loads company_data.json → Gemini API
                    → AI reply → Chat window
```

---

## 📁 Project Structure

```
AI-Customer-Support-Chatbot/
├── manage.py                        # Django management script
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variable template
├── .gitignore
│
├── static/                          # Static assets (root level)
│   ├── css/
│   │   └── style.css                # Primary stylesheet (widget, responsive, animations)
│   └── js/
│       └── main.js                  # Primary JS (widget logic, API calls, copy, menu)
│
├── templates/                       # HTML templates (root level)
│   └── chat.html                    # Main chat page template
│
├── chatbot_project/                 # Django project configuration
│   ├── settings.py                  # Settings (static files, apps, middleware)
│   ├── urls.py                      # Root URL config (/ and /api/)
│   └── wsgi.py
│
└── chatbot/                         # Main chatbot application
    ├── company_data.json            # ⭐ All company data (edit this to change business info)
    ├── services.py                  # Generic Gemini API logic (reads from JSON)
    ├── views.py                     # chat_page + chat_api endpoint
    ├── urls.py                      # App-level URL patterns (/api/chat/)
    └── apps.py
```

---

## 🏢 Demo Company — Smart Electronics

This project uses a **fictional company** for portfolio/demo purposes:

| Info | Details |
|------|---------|
| **Company** | Smart Electronics — Lahore, Pakistan |
| **Products** | Ceiling Fan (₨5,500), Pedestal Fan (₨7,200), Air Cooler (₨18,000), Exhaust Fan (₨3,200) |
| **Delivery** | Lahore: FREE · Other Cities: ₨250 · Time: 2–4 days |
| **Warranty** | Ceiling Fan: 2 years · Air Cooler: 1 year |
| **Hours** | Mon–Sat, 9:00 AM – 8:00 PM |
| **Contact** | 0300-1234567 · info@smartelectronics.pk |

> **💡 To change the company:** Just edit `chatbot/company_data.json` — no code changes required!

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.10+
- A [Google Gemini API Key](https://aistudio.google.com/app/apikey)

### 1. Clone the repository

```bash
git clone https://github.com/saqib-abdulraouf/AI-Customer-Support-Chatbot.git
cd AI-Customer-Support-Chatbot
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
DJANGO_DEBUG=True
```

### 5. Run migrations & start the server

```bash
python manage.py migrate
python manage.py runserver
```

### 6. Open in browser

Navigate to **http://127.0.0.1:8000/** — click the chat icon in the bottom-right corner to start chatting!

---

## 🔧 Customizing Company Data

All company information is stored in `chatbot/company_data.json`. To change the business:

```json
{
  "company_name": "Your Company Name",
  "tagline": "Your company description here.",
  "products": [
    { "name": "Product A", "price": "Rs. 1,000", "warranty": "1 Year" },
    { "name": "Product B", "price": "Rs. 2,500", "warranty": null }
  ],
  "delivery": {
    "local": "FREE",
    "other_cities": "Rs. 200",
    "delivery_time": "3–5 business days"
  },
  "business_hours": {
    "days": "Monday – Friday",
    "timing": "10:00 AM – 6:00 PM",
    "closed": "Saturday & Sunday"
  },
  "contact": {
    "phone": "0300-0000000",
    "email": "info@yourcompany.com",
    "location": "Your City, Pakistan"
  },
  "bot_behavior": [
    "Always respond in English.",
    "Be polite and professional.",
    "Never make up information."
  ]
}
```

Just edit this file and restart the server — **no Python code changes needed!**

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
  "reply": "Delivery in Lahore is completely FREE! For other cities, a delivery charge of Rs. 250 applies. Delivery typically takes 2–4 business days."
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
| **Config** | JSON-driven company data |
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

- [x] **JSON-Driven Company Data** — All business info loaded from `company_data.json`
- [ ] **RAG (Retrieval-Augmented Generation)** — Upload PDFs/catalogs, chunk & embed with LangChain, store vectors in ChromaDB/FAISS
- [ ] **WhatsApp Integration** — Connect via Twilio API for omnichannel support
- [ ] **Human Escalation** — "Talk to a human" button for low-confidence answers
- [ ] **User Authentication** — Session-based chat history persistence
- [ ] **Analytics Dashboard** — Track common queries, response times, and satisfaction
- [ ] **Django Admin Panel** — Edit company data from admin UI instead of JSON file

---

## 📝 Notes

- **CSRF** is exempted on `/api/chat/` since it's a public-facing API called via JS `fetch()` with no session/auth. Revisit this if you add user authentication.
- **Model Fallback**: The service layer tries models in order: `gemini-2.0-flash` → `gemini-flash-latest` → `gemini-2.5-flash`. If one is unavailable, it automatically falls through to the next.
- **Clipboard API** requires a secure context (HTTPS or localhost). A `document.execCommand('copy')` fallback is included for non-secure environments.
- **Company data** is loaded once at server start. Restart the server after editing `company_data.json`.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).