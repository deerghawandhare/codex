"""Data access layer with Supabase (if configured) or in-memory fallback."""
import os
from typing import Optional, List, Dict

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

_use_supabase = bool(SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL != "https://your-project-ref.supabase.co")

if _use_supabase:
    from supabase import create_client, Client
    _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("[Vineeta DB] Connected to Supabase")
else:
    _client = None
    print("[Vineeta DB] Using in-memory storage (Supabase not configured)")

# --- In-memory storage ---
_profiles: Dict[str, dict] = {}
_messages: Dict[str, List[dict]] = {}
_mock_notifications = [
    {
        "id": "pmmy-mudra",
        "title": "Pradhan Mantri Mudra Yojana (PMMY)",
        "deadline": "Open all year",
        "description": "Get a loan up to ₹10 lakh for your small business — no collateral needed. Apply at any bank near you.",
    },
    {
        "id": "stand-up-india",
        "title": "Stand-Up India Scheme",
        "deadline": "Open all year",
        "description": "Bank loan between ₹10 lakh and ₹1 crore for new businesses. Every bank branch must give at least one loan to a woman entrepreneur.",
    },
    {
        "id": "pmegp",
        "title": "PM Employment Generation Programme (PMEGP)",
        "deadline": "Applications reviewed monthly",
        "description": "Start a new small business and get part of the cost as a government subsidy. Extra subsidy for rural areas and women.",
    },
    {
        "id": "mahila-coir",
        "title": "Mahila Coir Yojana",
        "deadline": "Open all year",
        "description": "Free training plus up to 75% subsidy on spinning devices for women in coir-based rural industries.",
    },
    {
        "id": "jan-dhan",
        "title": "PM Jan Dhan Yojana — KYC update due",
        "deadline": "12 Aug 2026",
        "description": "Update your KYC details to keep your zero-balance account active.",
    },
]


# ---------- profiles ----------

def get_profile(user_id: str) -> Optional[dict]:
    if _use_supabase:
        res = _client.table("profiles").select("*").eq("user_id", user_id).execute()
        return res.data[0] if res.data else None
    return _profiles.get(user_id)


def upsert_profile(user_id: str, name: Optional[str], business_type: Optional[str], notes: Optional[str]) -> None:
    if _use_supabase:
        payload = {"user_id": user_id}
        if name is not None: payload["name"] = name
        if business_type is not None: payload["business_type"] = business_type
        if notes is not None: payload["notes"] = notes
        _client.table("profiles").upsert(payload, on_conflict="user_id").execute()
        return
    profile = _profiles.get(user_id, {"user_id": user_id})
    if name is not None: profile["name"] = name
    if business_type is not None: profile["business_type"] = business_type
    if notes is not None: profile["notes"] = notes
    _profiles[user_id] = profile


# ---------- chat history ----------

def save_message(user_id: str, role: str, content: str) -> None:
    if _use_supabase:
        _client.table("chat_messages").insert({"user_id": user_id, "role": role, "content": content}).execute()
        return
    _messages.setdefault(user_id, []).append({"role": role, "content": content})


def get_recent_messages(user_id: str, limit: int = 6) -> List[Dict]:
    if _use_supabase:
        res = (_client.table("chat_messages").select("role, content, created_at")
               .eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute())
        rows = list(reversed(res.data)) if res.data else []
        return [{"role": r["role"], "content": r["content"]} for r in rows]
    msgs = _messages.get(user_id, [])
    return [{"role": m["role"], "content": m["content"]} for m in msgs[-limit:]]


# ---------- notifications ----------

def get_notifications(user_id: str) -> List[Dict]:
    if _use_supabase:
        res = (_client.table("notifications").select("*")
               .or_(f"user_id.eq.{user_id},user_id.is.null").execute())
        return res.data or []
    return _mock_notifications
