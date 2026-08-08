"""Vineeta — AI financial-literacy chat assistant backend.

Run with:
    uvicorn main:app --reload
"""
from dotenv import load_dotenv

load_dotenv(override=True)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import database as db
from budget_logic import compute_budget_suggestion
from llm_client import get_reply
from schemas import (
    BudgetRequest,
    BudgetResponse,
    ChatRequest,
    ChatResponse,
    NotificationItem,
    NotificationsResponse,
    ProfileRequest,
    ProfileResponse,
)

app = FastAPI(title="Vineeta API", description="AI financial-literacy chat assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message cannot be empty")

    profile = db.get_profile(req.user_id)
    history = db.get_recent_messages(req.user_id, limit=6)

    try:
        reply = get_reply(req.message, req.language, profile, history)
    except Exception as exc:  # LLM/network failure shouldn't 500 silently
        raise HTTPException(status_code=502, detail=f"LLM provider error: {exc}")

    db.save_message(req.user_id, "user", req.message)
    db.save_message(req.user_id, "assistant", reply)

    return ChatResponse(reply=reply, language=req.language)


@app.post("/api/profile", response_model=ProfileResponse)
def update_profile(req: ProfileRequest):
    db.upsert_profile(req.user_id, req.name, req.business_type, req.notes)
    return ProfileResponse(status="ok")


@app.get("/api/notifications", response_model=NotificationsResponse)
def notifications(user_id: str):
    rows = db.get_notifications(user_id)
    items = [
        NotificationItem(
            id=str(row["id"]),
            title=row["title"],
            deadline=row.get("deadline"),
            description=row.get("description"),
        )
        for row in rows
    ]
    return NotificationsResponse(notifications=items)


@app.post("/api/budget", response_model=BudgetResponse)
def budget(req: BudgetRequest):
    suggestion, recommended_savings = compute_budget_suggestion(req.income, req.expenses)
    return BudgetResponse(suggestion=suggestion, recommended_savings=recommended_savings)


YOUTUBE_DATA = {
    "categories": [
        "Saving Money", "Budgeting", "Government Schemes", "Insurance",
        "Loans", "Farming Finance", "Women's Entrepreneurship", "Small Business",
        "Digital Payments", "UPI", "Investments", "Self Help Groups"
    ],
    "recommended": [
        {
            "id": "rec-1",
            "title": "छोटी आदतें, बड़ी बचत – आसान तरीके से शुरू करें",
            "duration": "6:45",
            "language": "Hindi",
            "thumbnailBg": "from-teal-800 to-teal-600",
            "views": "45K views"
        },
        {
            "id": "rec-2",
            "title": "सरकारी योजनाओं का लाभ कैसे उठाएं? पूरी जानकारी",
            "duration": "8:12",
            "language": "Hindi",
            "thumbnailBg": "from-amber-700 to-amber-500",
            "views": "82K views"
        },
        {
            "id": "rec-3",
            "title": "महिलाओं के लिए टॉप 5 बिजनेस आइडियाज़",
            "duration": "7:30",
            "language": "Hindi",
            "thumbnailBg": "from-orange-700 to-amber-600",
            "views": "31K views"
        }
    ],
    "continueWatching": [
        {
            "id": "cw-1",
            "title": "UPI से पेमेंट कैसे करें? पूरी जानकारी",
            "duration": "5:20",
            "language": "Hindi",
            "progress": 60,
            "thumbnailBg": "from-cyan-700 to-teal-800"
        },
        {
            "id": "cw-2",
            "title": "निवेश की शुरुआत कैसे करें? (2024 गाइड)",
            "duration": "6:15",
            "language": "Hindi",
            "progress": 40,
            "thumbnailBg": "from-emerald-700 to-green-800"
        }
    ],
    "recentlyViewed": [
        {
            "id": "rv-1",
            "title": "बीमा क्यों ज़रूरी है? समझें आसान भाषा में",
            "duration": "4:50",
            "language": "Hindi"
        },
        {
            "id": "rv-2",
            "title": "छोटा बिजनेस कैसे शुरू करें? – स्टेप बाय स्टेप गाइड",
            "duration": "6:40",
            "language": "Hindi"
        },
        {
            "id": "rv-3",
            "title": "डिजिटल पेमेंट के फायदे और सुरक्षा टिप्स",
            "duration": "4:35",
            "language": "Hindi"
        }
    ]
}

USER_PROFILE = {
    "name": "Priya Sharma",
    "phone": "+91 98765 43210",
    "primaryIncome": "Salary",
    "secondaryIncome": "Freelancing",
    "tagline": "Welcome back! You're building a stronger financial future."
}


@app.get("/api/youtube/content")
def get_youtube_content():
    return {
        "success": True,
        "data": YOUTUBE_DATA
    }


@app.get("/api/user/profile")
def get_user_profile():
    return {
        "success": True,
        "profile": USER_PROFILE
    }

