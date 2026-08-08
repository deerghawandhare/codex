# Vineeta — Financial-Literacy Chat Assistant (Backend)

FastAPI backend for "Vineeta," an AI companion that helps rural Indian women with
budgeting, saving habits, and basic financial-inclusion info — in Hindi, Marathi,
or English. No authentication: `user_id` is assumed to already be provided by
whatever client (app/SMS/WhatsApp gateway) sits in front of this.

## 1. Install

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in your keys below
```

## 2. Get free API keys

- **Groq** (default, fast + generous free tier): https://console.groq.com → API Keys.
  Groq deprecated the old `llama-3.3-70b-versatile` / `llama-3.1-8b-instant` models in
  mid-2026 — this project defaults to `openai/gpt-oss-20b`, their recommended free
  replacement. Change `GROQ_MODEL` in `.env` if you want `openai/gpt-oss-120b` for
  higher quality.
- **Gemini** (alternative): https://aistudio.google.com → Get API key. Free-tier model
  names shift fairly often — double check the current free lineup at
  ai.google.dev/pricing and update `GEMINI_MODEL` if needed.

Set `LLM_PROVIDER=groq` or `LLM_PROVIDER=gemini` in `.env` to pick one.

## 3. Set up Supabase (free tier)

Create a project at https://supabase.com, then in the SQL editor run:

```sql
create table profiles (
  user_id text primary key,
  name text,
  business_type text,
  notes text,
  updated_at timestamptz default now()
);

create table chat_messages (
  id bigint generated always as identity primary key,
  user_id text not null,
  role text not null,       -- 'user' or 'assistant'
  content text not null,
  created_at timestamptz default now()
);

create table notifications (
  id bigint generated always as identity primary key,
  user_id text,              -- null = shown to every user
  title text not null,
  deadline text,
  description text
);

-- a couple of example global notifications
insert into notifications (user_id, title, deadline, description) values
  (null, 'Update your profile', null, 'Tell Vineeta a bit about your work so advice fits you better.'),
  (null, 'Post Office savings scheme review', null, 'A good time each quarter to check current interest rates with your post office.');
```

Copy your project's **URL** and **anon/service key** (Project Settings → API) into
`.env` as `SUPABASE_URL` / `SUPABASE_KEY`.

> This prototype has no auth, so the notifications query trusts `user_id` as given.
> Before going to production, add row-level security / auth so one user can't read
> another's data.

## 4. Run

```bash
uvicorn main:app --reload
```

Server runs at `http://localhost:8000`. Interactive docs at `/docs`.

## 5. Endpoints & curl examples

### POST /api/chat
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" -d '{"user_id":"u1","message":"Namaste, mujhe bachat shuru karni hai","language":"hi"}'
```

### POST /api/profile
```bash
curl -X POST http://localhost:8000/api/profile \
  -H "Content-Type: application/json" -d '{"user_id":"u1","name":"Radha","business_type":"tailoring"}'
```

### GET /api/notifications
```bash
curl "http://localhost:8000/api/notifications?user_id=u1"
```

### POST /api/budget
```bash
curl -X POST http://localhost:8000/api/budget \
  -H "Content-Type: application/json" -d '{"income":15000,"expenses":12000}'
```

## Notes on the Vineeta persona

The system prompt (in `llm_client.py`) is written so Vineeta:
- Never claims to be a certified/trained financial advisor, even if pressed.
- Points the user to their bank, post office, CSC, or an official site to verify
  any specific numbers (interest rates, eligibility, deadlines).
- Asks at most **one** profiling question per turn, and only about fields it
  doesn't already know (pulled from Supabase `profiles`).
- Replies briefly, in plain language, in whichever of `hi` / `mr` / `en` was requested.
- Refuses to collect PINs/OTPs/passwords/full account numbers and tells the user
  never to share those with anyone.

`/api/chat` also stores the last few turns in `chat_messages` and feeds them back
in as short-term memory, so Vineeta doesn't repeat questions it already asked.
This isn't in the original spec's four endpoints but makes the "ask one question
at a time" persona behavior actually work across turns — remove `db.save_message`
calls in `main.py` if you'd rather keep `/api/chat` fully stateless.
