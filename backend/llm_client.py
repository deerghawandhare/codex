"""Vineeta's persona (system prompt) with fluent Marathi, Hindi, and English support."""
import os
from typing import Optional, List, Dict

LANGUAGE_NAMES = {
    "hi": "Hindi (हिंदी)",
    "mr": "Marathi (मराठी)",
    "en": "English",
}

LANGUAGE_INSTRUCTIONS = {
    "hi": "आप पूरी तरह से प्राकृतिक, सरल और स्पष्ट हिंदी में ही उत्तर दें। उत्तर में 'दीदी' की तरह अपनेपन और आदर की भाषा का प्रयोग करें।",
    "mr": "तुम्ही पूर्णपणे अस्खलित, सोप्या आणि नैसर्गिक शुद्ध मराठी भाषेतच उत्तर द्या (उदा. 'नमस्कार!', 'बचत', 'कर्ज', 'योजना'). उत्तर अत्यंत आपुलकीने आणि स्पष्ट मराठीतच लिहा.",
    "en": "Respond fluently in clear, simple English using a warm, encouraging tone as an elder sister.",
}

BASE_SYSTEM_PROMPT = """You are "Vineeta," a warm, friendly financial-literacy companion for rural Indian women. You help with everyday money matters: budgeting, saving habits, basic banking, and understanding common government financial-inclusion schemes.

CRITICAL LANGUAGE REQUIREMENT:
- You MUST respond ONLY in {language_name}.
- {language_instruction}

WHO YOU ARE:
- You speak like a caring, respected elder sister (didi) or trusted friend — warm, patient, encouraging. Never sound preachy, superior, or judgmental.
- Use simple, everyday words. Explain technical terms in one short sentence.
- Keep replies short and conversational — 2-3 sentences.

GETTING TO KNOW THE USER:
{profile_context}
"""


def _profile_context(profile: Optional[dict]) -> str:
    if not profile:
        return "You don't know anything about this user yet. Start by warmly asking their name."
    return "User profile is active."


def build_system_prompt(language: str, profile: Optional[dict]) -> str:
    lang_name = LANGUAGE_NAMES.get(language, LANGUAGE_NAMES["en"])
    lang_inst = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["en"])
    return BASE_SYSTEM_PROMPT.format(
        language_name=lang_name,
        language_instruction=lang_inst,
        profile_context=_profile_context(profile),
    )


def call_gemini(system_prompt: str, history: List[Dict], user_message: str) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    model = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

    contents = []
    for turn in history:
        role = "model" if turn["role"] == "assistant" else "user"
        contents.append(types.Content(role=role, parts=[types.Part(text=turn["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part(text=user_message)]))

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.6,
            max_output_tokens=350,
        ),
    )
    return response.text.strip()


def call_groq(system_prompt: str, history: List[Dict], user_message: str) -> str:
    from groq import Groq

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.6,
        max_tokens=350,
    )
    return completion.choices[0].message.content.strip()


def get_reply(message: str, language: str, profile: Optional[dict], history: List[Dict]) -> str:
    system_prompt = build_system_prompt(language, profile)
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    has_groq = bool(os.getenv("GROQ_API_KEY") and os.getenv("GROQ_API_KEY") != "your_groq_key_here")
    has_gemini = bool(os.getenv("GEMINI_API_KEY") and os.getenv("GEMINI_API_KEY") != "your_gemini_key_here")

    if provider == "gemini" and has_gemini:
        return call_gemini(system_prompt, history, message)
    if has_groq:
        return call_groq(system_prompt, history, message)
    if has_gemini:
        return call_gemini(system_prompt, history, message)

    return _mock_reply(message, language)


def _mock_reply(message: str, language: str) -> str:
    text = message.lower()
    replies = {
        "en": {
            "budget": "Let's build a simple budget. Tell me your monthly income and expenses.",
            "loan": "For loan guidance, tell me what amount you need and what it's for.",
            "default": "Namaste! I'm Vineeta, your AI financial guide.",
        },
        "hi": {
            "budget": "चलिए एक आसान बजट बनाते हैं! अपनी मासिक कमाई और खर्च बताएं।",
            "loan": "ऋण मार्गदर्शन के लिए बताएं आपको कितनी राशि चाहिए।",
            "default": "नमस्ते! मैं विनीता हूं, आपकी एआई वित्तीय गाइड।",
        },
        "mr": {
            "budget": "चला एक सोपा अर्थसंकल्प बनवूया! तुमचे मासिक उत्पन्न आणि खर्च सांगा.",
            "loan": "कर्ज मार्गदर्शनासाठी सांगा तुम्हाला किती रक्कमेची गरज आहे.",
            "default": "नमस्कार! मी विनिता आहे, तुमची AI आर्थिक मार्गदर्शक.",
        },
    }
    set_r = replies.get(language, replies["en"])
    if "budget" in text or "बजट" in text or "बजेट" in text: return set_r["budget"]
    if "loan" in text or "ऋण" in text or "कर्ज" in text: return set_r["loan"]
    return set_r["default"]
