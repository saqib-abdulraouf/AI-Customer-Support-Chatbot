# 🤖 AI Customer Support Chatbot — Smart Electronics

A modern, fully responsive AI-powered customer support chatbot built for **Smart Electronics** (a demo electronics store in Lahore) using **Django** and **Google Gemini API**. Designed as a floating website widget with a premium, professional UI.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-green?logo=django&logoColor=white)
![Gemini](https://img.shields.io/badge/Google_Gemini-API-orange?logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

- **Google Gemini AI** — Powered by `gemini-2.0-flash` with automatic model fallback
- **RAG Architecture (PDF Upload)** — Upload PDFs via Django Admin, extract text with PyMuPDF, chunk text, generate vector embeddings with Gemini `text-embedding-004`, and store in persistent ChromaDB
- **JSON-Driven Company Data** — Modular business knowledge files stored in `knowledge/` directory
- **Floating Chat Widget** — Bottom-right launcher icon that opens a sleek chat window
- **Smooth Animations** — Spring-style open/close transitions for the chat widget
- **Responsive Design** — Full-screen on mobile (≤600px), floating card on desktop (440×640px)
- **Copy to Clipboard** — Hover over any message to reveal a copy icon (icon-only, no text)
- **Quick Suggestions** — Horizontal scrollable suggestion chips (Delivery Info, Order Tracking, Payment Options)
- **Menu Drawer** — Hamburger menu (☰) with options for New Conversation, Recent Chats, and Clear History
- **Conversation History** — Chat context is maintained per session for coherent multi-turn dialogue
- **Strictly English** — All AI responses are in fluent, professional English regardless of input language

---

## 🏗️ Architecture & RAG Flow

```
                        Admin
                          │
                      Upload PDF
                          │
                    Django Backend
                          │
                Extract Text (PyMuPDF)
                          │
                  Split into Chunks
                          │
             Generate Embeddings (Gemini)
                          │
                  Store in ChromaDB
                          │
────────────────────────────────────────────────────

                  Customer asks question
                          │
                Similar Chunks Search
                          │
             Send Context + Question
                          │
                      Gemini
                          │
                       Answer
```

---

## 📁 Project Structure

```
AI-Customer-Support-Chatbot/
├── manage.py                        # Django management script
├── requirements.txt                 # Python dependencies (PyMuPDF, ChromaDB, Gemini, Django)
├── .env.example                     # Environment variable template
├── .gitignore
│
├── chroma_db/                       # Persistent ChromaDB vector database
├── media/                           # Uploaded PDF document storage
│
├── knowledge/                       # ⭐ Modular business data (auto-loaded)
│   ├── company.json                 # Company name, contact, hours, bot behavior
│   ├── products.json                # Product catalog (names, prices, warranty)
│   ├── delivery.json                # Delivery policy & charges
│   ├── faq.json                     # Frequently asked questions
│   └── return_policy.json           # Return & refund policy
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
│   ├── settings.py                  # Settings (media files, static, apps, middleware)
│   ├── urls.py                      # Root URL config (/admin/, /, and /api/)
│   └── wsgi.py
│
└── chatbot/                         # Main chatbot application
    ├── admin.py                     # Django Admin for PDF upload & vector indexing
    ├── models.py                    # PDFDocument model with auto-indexing signals
    ├── rag_service.py               # PyMuPDF extraction, chunking, Gemini embeddings & ChromaDB
    ├── services.py                  # Gemini LLM orchestration + RAG context injection
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

## 🔧 Customizing Knowledge Base

All business information is stored as modular `.json` files inside the `knowledge/` directory:

- `knowledge/company.json` — Store metadata, business hours, contact info, and custom bot behavior rules.
- `knowledge/products.json` — Product details, pricing, categories, and warranty terms.
- `knowledge/delivery.json` — City-wise shipping rates, delivery timeframes, and dispatch rules.
- `knowledge/faq.json` — Frequently asked questions (e.g. COD, installation, store visits).
- `knowledge/return_policy.json` — Return window, conditions, and refund policies.

> **💡 Modular Architecture:** You can drop **any new `.json` file** (e.g. `discounts.json`, `branches.json`, `terms.json`) into the `knowledge/` folder. The chatbot automatically detects, parses, and integrates new files into its knowledge base upon server restart — **no Python code edits required!**


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
| **AI Model** | Google Gemini API (`gemini-2.0-flash` + `text-embedding-004`) |
| **RAG Vector Database** | ChromaDB (persistent local vector store) |
| **PDF Processing** | PyMuPDF (`fitz`) text extraction |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Icons** | Font Awesome 6 |
| **Database** | SQLite (default) |
| **Config** | Modular JSON-driven knowledge base |
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

- [x] **JSON-Driven Company Data** — Modular knowledge base in `knowledge/` folder
- [x] **RAG (Retrieval-Augmented Generation)** — Upload PDFs in Django Admin, extract text with PyMuPDF, embed with Gemini (`text-embedding-004`), and store in ChromaDB
- [x] **Django Admin Panel** — Manage PDF documents and trigger vector re-indexing directly from `/admin/`
- [ ] **WhatsApp Integration** — Connect via Twilio API for omnichannel support
- [ ] **Human Escalation** — "Talk to a human" button for low-confidence answers
- [ ] **User Authentication** — Session-based chat history persistence
- [ ] **Analytics Dashboard** — Track common queries, response times, and satisfaction

---

## 📝 Notes

- **CSRF** is exempted on `/api/chat/` since it's a public-facing API called via JS `fetch()` with no session/auth. Revisit this if you add user authentication.
- **Model Fallback**: The service layer tries models in order: `gemini-2.0-flash` → `gemini-flash-latest` → `gemini-2.5-flash`. If one is unavailable, it automatically falls through to the next.
- **Clipboard API** requires a secure context (HTTPS or localhost). A `document.execCommand('copy')` fallback is included for non-secure environments.
- **Company data** is loaded once at server start. Restart the server after editing `company_data.json`.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).