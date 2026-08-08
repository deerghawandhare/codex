# codex
# Vineeta 3.0 — AI Financial-Literacy Chat Assistant

Vineeta 3.0 is an AI financial-literacy companion for rural Indian women, providing budgeting advice, loan guidance, and information on government schemes in Hindi, Marathi, and English.

## Project Structure

```
vinita3/
├── backend/            # FastAPI backend (LLM integration + endpoints)
│   ├── main.py         # App entry point (/api/chat, /api/notifications, /api/budget, /api/profile)
│   ├── llm_client.py   # Gemini & Groq LLM client with Vineeta persona
│   ├── database.py     # Supabase client with in-memory fallback
│   ├── schemas.py      # Pydantic models
│   └── .env            # Environment configuration & API keys
└── frontend/           # React 19 + Vite + TailwindCSS frontend
    ├── src/
    │   ├── VineetaApp.jsx  # Main interactive UI component
    │   └── App.jsx
    └── vite.config.js  # Vite server proxy (/api -> http://localhost:8000)
```

## How to Run

### 1. Start the Backend (Port 8000)
```powershell
cd backend
uvicorn main:app --reload --port 8000
```
Interactive API docs are available at `http://localhost:8000/docs`.

### 2. Start the Frontend Dev Server
```powershell
cd frontend
npm.cmd run dev
```
Open `http://localhost:5173` in your browser.

## API Endpoints Summary

- **`POST /api/chat`**: Accepts `{ user_id, message, language }` and returns `{ reply, language }` generated live by Gemini/Groq.
- **`GET /api/notifications`**: Retrieves active financial alerts and scheme updates for the given `user_id`.
- **`POST /api/budget`**: Accepts `{ income, expenses }` and returns personalized budget suggestions and savings target.
- **`POST /api/profile`**: Upserts user name, business type, and notes.

