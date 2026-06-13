"""
Aarambha Haq — Telegram Bot (Smart Edition)
Free scheme eligibility checker for 22 Indian languages.
Features: free-text NLP profile parsing, natural language search, follow-up Q&A.
Run: python3 bots/telegram_bot.py
"""
from __future__ import annotations

import json
import os
import re
import threading
from typing import Any

try:
    from rapidfuzz import process as fuzz_process, fuzz
    _FUZZY = True
except ImportError:
    _FUZZY = False

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ── Config ───────────────────────────────────────────────────────────────────
BOT_TOKEN    = os.environ.get("TELEGRAM_BOT_TOKEN", "")
API_BASE     = os.environ.get("HAQ_API_URL", "http://localhost:8097")
DB_NAME      = os.environ.get("HAQ_DB", "aarambha_haq")
DB_USER      = os.environ.get("HAQ_DB_USER", "aarambha_haq")

# ── Groq-only LLM config ─────────────────────────────────────────────────────
GROQ_KEY  = os.environ.get("GROQ_KEY", "")
GROQ_BASE = "https://api.groq.com/openai/v1/"

# Waterfall: fastest/most-quota first → heavier models as fallback on 429
GROQ_MODELS = [
    "llama-3.1-8b-instant",                    # 14.4K RPD — primary
    "llama-3.3-70b-versatile",                  # 1K RPD   — smarter fallback
    "meta-llama/llama-4-scout-17b-16e-instruct",# 1K RPD   — last resort
]


def llm_call(prompt: str, system: str = "", json_mode: bool = False) -> str | None:
    """Groq waterfall: tries each model in order, skips on 429, returns first success."""
    if not GROQ_KEY:
        return None
    payload: dict = {"messages": [], "max_tokens": 512}
    if system:
        payload["messages"].append({"role": "system", "content": system})
    payload["messages"].append({"role": "user", "content": prompt})
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    for model in GROQ_MODELS:
        try:
            r = requests.post(
                f"{GROQ_BASE}chat/completions",
                headers={"Authorization": f"Bearer {GROQ_KEY}"},
                json={**payload, "model": model},
                timeout=12,
            )
            if r.ok:
                return r.json()["choices"][0]["message"]["content"]
            if r.status_code != 429:
                break  # non-rate-limit error — no point retrying other models
        except Exception:
            pass
    return None


# ── Language labels ───────────────────────────────────────────────────────────
LANG_OPTIONS = [
    ("hi",  "हिन्दी"),
    ("en",  "English"),
    ("mr",  "मराठी"),
    ("bn",  "বাংলা"),
    ("te",  "తెలుగు"),
    ("ta",  "தமிழ்"),
    ("gu",  "ગુજરાતી"),
    ("kn",  "ಕನ್ನಡ"),
    ("pa",  "ਪੰਜਾਬੀ"),
    ("ml",  "മലയാളം"),
    ("or",  "ଓଡ଼ିଆ"),
]

# ── UI strings (hi / en only for bot UI; scheme content comes from translations table) ──
UI = {
    "hi": {
        "welcome":      "🇮🇳 *Aarambha Haq में आपका स्वागत है!*\n\nसरकारी योजनाओं की मुफ्त जानकारी — आपकी भाषा में।\n\nपहले अपनी भाषा चुनें:",
        "menu":         "आप क्या करना चाहते हैं?",
        "check_lbl":    "✅ पात्रता जांचें",
        "search_lbl":   "🔍 योजना खोजें",
        "rights_lbl":   "⚖️ अपने अधिकार",
        "lang_lbl":     "🌐 भाषा बदलें",
        "ask_state":    "📍 आपका राज्य क्या है?\n\nराज्य का नाम टाइप करें (जैसे: UP, Bihar, Maharashtra)",
        "ask_age":      "🎂 आपकी उम्र क्या है?\n\nसिर्फ नंबर लिखें (जैसे: 35)",
        "ask_gender":   "👤 आप कौन हैं?",
        "female":       "👩 महिला",
        "male":         "👨 पुरुष",
        "other":        "🧑 अन्य",
        "ask_caste":    "📋 आपकी श्रेणी क्या है?",
        "ask_income":   "💰 परिवार की सालाना आय?",
        "ask_flags":    "अन्य जानकारी (जो लागू हो वो सब चुनें, फिर ✅ Done दबाएं):",
        "done_flags":   "✅ Done",
        "searching":    "🔍 आपके लिए योजनाएं खोज रहे हैं...",
        "results_hdr":  "🎯 *आपके लिए {n} योजनाएं मिलीं!*\n",
        "no_results":   "😔 आपकी जानकारी से कोई योजना नहीं मिली।\nफ़िल्टर बदलें या वेबसाइट पर देखें:\nhaq.aarambhax.in",
        "apply_btn":    "📋 आवेदन करें",
        "more_btn":     "और देखें →",
        "search_prompt":"योजना का नाम या विषय टाइप करें\n(जैसे: scholarship, छात्रवृत्ति, kisan, महिला)",
        "rights_hdr":   "⚖️ *आपके अधिकार*\n\nश्रेणी चुनें:",
        "invalid_age":  "⚠️ कृपया सही उम्र डालें (1-120)",
        "lang_changed": "✅ भाषा बदल गई!",
        "website_link": "🌐 पूरी वेबसाइट: haq.aarambhax.in",
    },
    "en": {
        "welcome":      "🇮🇳 *Welcome to Aarambha Haq!*\n\nFree government scheme finder in your language.\n\nChoose your language:",
        "menu":         "What would you like to do?",
        "check_lbl":    "✅ Check Eligibility",
        "search_lbl":   "🔍 Search Schemes",
        "rights_lbl":   "⚖️ Know Your Rights",
        "lang_lbl":     "🌐 Change Language",
        "ask_state":    "📍 What is your state?\n\nType the state name (e.g. UP, Bihar, Maharashtra)",
        "ask_age":      "🎂 What is your age?\n\nType a number (e.g. 35)",
        "ask_gender":   "👤 Who are you?",
        "female":       "👩 Female",
        "male":         "👨 Male",
        "other":        "🧑 Other",
        "ask_caste":    "📋 What is your category?",
        "ask_income":   "💰 Annual family income?",
        "ask_flags":    "Any of the following apply? (select all, then press ✅ Done):",
        "done_flags":   "✅ Done",
        "searching":    "🔍 Finding schemes for you...",
        "results_hdr":  "🎯 *Found {n} schemes for you!*\n",
        "no_results":   "😔 No schemes found for your profile.\nTry changing filters or visit:\nhaq.aarambhax.in",
        "apply_btn":    "📋 Apply",
        "more_btn":     "View More →",
        "search_prompt":"Type a scheme name or topic\n(e.g. scholarship, kisan, housing, mahila)",
        "rights_hdr":   "⚖️ *Your Rights*\n\nChoose a category:",
        "invalid_age":  "⚠️ Please enter a valid age (1-120)",
        "lang_changed": "✅ Language changed!",
        "website_link": "🌐 Full website: haq.aarambhax.in",
    },
}

INCOME_OPTIONS = {
    "hi": [
        ("0–1 लाख", 80000),
        ("1–3 लाख", 200000),
        ("3–6 लाख", 450000),
        ("6–10 लाख", 800000),
        ("10+ लाख", 1500000),
    ],
    "en": [
        ("0–1 Lakh", 80000),
        ("1–3 Lakh", 200000),
        ("3–6 Lakh", 450000),
        ("6–10 Lakh", 800000),
        ("10+ Lakh", 1500000),
    ],
}

CASTE_OPTIONS = {
    "hi": [("SC", "SC"), ("ST", "ST"), ("OBC", "OBC"), ("EWS", "EWS"), ("General/सामान्य", "General")],
    "en": [("SC", "SC"), ("ST", "ST"), ("OBC", "OBC"), ("EWS", "EWS"), ("General", "General")],
}

FLAG_OPTIONS = {
    "hi": [
        ("विधवा", "widow"),
        ("दिव्यांग", "disability"),
        ("अल्पसंख्यक", "minority"),
        ("BPL कार्ड", "bpl"),
        ("गर्भवती", "pregnant"),
    ],
    "en": [
        ("Widow", "widow"),
        ("Disabled", "disability"),
        ("Minority", "minority"),
        ("BPL Card", "bpl"),
        ("Pregnant", "pregnant"),
    ],
}

RIGHTS_CATEGORIES = {
    "hi": [
        ("mahila-haq",     "👩 महिला हक"),
        ("gharelu-hinsa",  "🛡️ घरेलू हिंसा"),
        ("prasuti",        "🤱 प्रसूति"),
        ("talak",          "⚖️ तलाक"),
        ("sampatti",       "🏠 संपत्ति"),
        ("pension",        "👴 पेंशन"),
        ("legal-aid",      "🧑‍⚖️ कानूनी सहायता"),
        ("shiksha-rozgar", "📚 शिक्षा/रोज़गार"),
    ],
    "en": [
        ("mahila-haq",     "👩 Women's Rights"),
        ("gharelu-hinsa",  "🛡️ Domestic Violence"),
        ("prasuti",        "🤱 Maternity"),
        ("talak",          "⚖️ Divorce/Family"),
        ("sampatti",       "🏠 Property"),
        ("pension",        "👴 Pension"),
        ("legal-aid",      "🧑‍⚖️ Legal Aid"),
        ("shiksha-rozgar", "📚 Education/Employment"),
    ],
}


# ── State normalizer + rule-based profile extractor ─────────────────────────
STATE_MAP = {
    "up": "Uttar Pradesh", "uttar pradesh": "Uttar Pradesh",
    "mp": "Madhya Pradesh", "madhya pradesh": "Madhya Pradesh",
    "mh": "Maharashtra", "maharashtra": "Maharashtra",
    "rj": "Rajasthan", "rajasthan": "Rajasthan",
    "wb": "West Bengal", "west bengal": "West Bengal",
    "br": "Bihar", "bihar": "Bihar",
    "tn": "Tamil Nadu", "tamil nadu": "Tamil Nadu",
    "ka": "Karnataka", "karnataka": "Karnataka",
    "gj": "Gujarat", "gujarat": "Gujarat",
    "ap": "Andhra Pradesh", "andhra pradesh": "Andhra Pradesh",
    "ts": "Telangana", "telangana": "Telangana",
    "od": "Odisha", "odisha": "Odisha", "orissa": "Odisha",
    "kl": "Kerala", "kerala": "Kerala",
    "pb": "Punjab", "punjab": "Punjab",
    "hr": "Haryana", "haryana": "Haryana",
    "jh": "Jharkhand", "jharkhand": "Jharkhand",
    "cg": "Chhattisgarh", "chhattisgarh": "Chhattisgarh",
    "uk": "Uttarakhand", "uttarakhand": "Uttarakhand",
    "hp": "Himachal Pradesh", "himachal pradesh": "Himachal Pradesh",
    "as": "Assam", "assam": "Assam",
    "jk": "Jammu and Kashmir", "jammu kashmir": "Jammu and Kashmir",
    "dl": "Delhi", "delhi": "Delhi",
    "ga": "Goa", "goa": "Goa",
    "sk": "Sikkim", "sikkim": "Sikkim",
    "mn": "Manipur", "manipur": "Manipur",
    "ml": "Meghalaya", "meghalaya": "Meghalaya",
    "tr": "Tripura", "tripura": "Tripura",
    "nl": "Nagaland", "nagaland": "Nagaland",
    "mz": "Mizoram", "mizoram": "Mizoram",
    "ar": "Arunachal Pradesh", "arunachal pradesh": "Arunachal Pradesh",
    # UTs often mentioned
    "py": "Puducherry", "puducherry": "Puducherry", "pondicherry": "Puducherry",
    "ch": "Chandigarh", "chandigarh": "Chandigarh",
    "ld": "Ladakh", "ladakh": "Ladakh",
    "dd": "Dadra and Nagar Haveli", "daman": "Daman and Diu",
    "an": "Andaman and Nicobar", "lk": "Lakshadweep",
}

def _normalize_state(text: str) -> str:
    key = text.strip().lower()
    return STATE_MAP.get(key, text.title())


# All canonical state names (values from STATE_MAP, deduplicated)
_ALL_STATES = list(dict.fromkeys(STATE_MAP.values()))
# Also include common Hindi state spellings for fuzzy match
_STATE_ALIASES = {
    "उत्तर प्रदेश": "Uttar Pradesh", "यूपी": "Uttar Pradesh",
    "मध्य प्रदेश": "Madhya Pradesh", "एमपी": "Madhya Pradesh",
    "महाराष्ट्र": "Maharashtra", "राजस्थान": "Rajasthan",
    "बिहार": "Bihar", "गुजरात": "Gujarat", "तमिलनाडु": "Tamil Nadu",
    "कर्नाटक": "Karnataka", "पश्चिम बंगाल": "West Bengal",
    "हरियाणा": "Haryana", "पंजाब": "Punjab", "केरल": "Kerala",
    "उत्तराखंड": "Uttarakhand", "झारखंड": "Jharkhand",
    "छत्तीसगढ़": "Chhattisgarh", "हिमाचल": "Himachal Pradesh",
    "असम": "Assam", "दिल्ली": "Delhi", "गोवा": "Goa",
    "तेलंगाना": "Telangana", "आंध्र": "Andhra Pradesh",
    "ओडिशा": "Odisha",
}

_GENDER_FEMALE = {
    "महिला", "औरत", "स्त्री", "लड़की", "बेटी", "माँ", "मां",
    "विधवा", "गर्भवती", "female", "woman", "girl", "lady", "wife",
    "widow", "pregnant", "she", "her",
}
_GENDER_MALE = {
    "पुरुष", "आदमी", "लड़का", "बेटा", "पिता", "किसान",
    "male", "man", "boy", "husband", "he", "his", "farmer",
}

# Caste patterns: short codes (sc/st/obc/ews) must match as whole words via regex
_CASTE_RE = {
    "SC":      re.compile(r"\bsc\b|\bscheduled\s+caste\b|दलित|अनुसूचित\s*जाति", re.IGNORECASE),
    "ST":      re.compile(r"\bst\b|\bscheduled\s+tribe\b|आदिवासी|अनुसूचित\s*जनजाति", re.IGNORECASE),
    "OBC":     re.compile(r"\bobc\b|\bother\s+backward\b|पिछड़ा|पिछड़े", re.IGNORECASE),
    "EWS":     re.compile(r"\bews\b|\beconomically\s+weaker\b|ईडब्ल्यूएस", re.IGNORECASE),
    "General": re.compile(r"\bgeneral\b|\bunreserved\b|सामान्य", re.IGNORECASE),
}

# Flag patterns: use regex for word-boundary safety
_FLAG_RE = {
    "widow":      re.compile(r"\bwid\w{1,4}\b|विधवा|vidhwa|bidhwa|पति नहीं", re.IGNORECASE),
    "disability": re.compile(r"\bdisabilit\w+\b|\bdisabled\b|\bhandicap\w*\b|दिव्यांग|विकलांग", re.IGNORECASE),
    "minority":   re.compile(r"\bminority\b|\bmuslim\b|\bchristian\b|\bsikh\b|अल्पसंख्यक|मुस्लिम|ईसाई|सिख", re.IGNORECASE),
    "bpl":        re.compile(r"\bbpl\b|गरीबी रेखा|below poverty|राशन कार्ड|ration card", re.IGNORECASE),
    "pregnant":   re.compile(r"\bpregnant\b|\bpregnancy\b|गर्भवती|प्रेग्नेंट", re.IGNORECASE),
}

# Income in Hindi/Hinglish: "1.5 लाख", "2 lakh", "50000", "50k", "50 हज़ार"
_RE_INCOME_LAKH  = re.compile(r"(\d+(?:\.\d+)?)\s*(?:lakh|लाख|lac)", re.IGNORECASE)
_RE_INCOME_HAZAR = re.compile(r"(\d+(?:\.\d+)?)\s*(?:हज़ार|हजार|thousand|k\b)", re.IGNORECASE)
_RE_INCOME_BARE  = re.compile(r"(?:income|आय|salary|वेतन)\s*[:\-]?\s*(\d{4,7})", re.IGNORECASE)

# Age: "35 साल", "40 saal", "age 35", "35 year/yr/yrs", "उम्र 35", "I am 35"
_RE_AGE = re.compile(
    r"(?:age|उम्र|āyu|aayu|i\s+am)\s*[:\-]?\s*(\d{1,3})"
    r"|(\d{1,3})\s*(?:साल|saal|sal|year|yr|yrs|वर्ष)",
    re.IGNORECASE | re.UNICODE,
)
# Fallback: bare standalone number (used only when other fields found)
_RE_BARE_NUM = re.compile(r"(?<!\d)(\d{1,3})(?!\d)")


def _fuzzy_state(word: str) -> str | None:
    """Try to identify an Indian state from a single word (handles typos)."""
    low = word.lower().strip()
    if not low or len(low) < 2:
        return None

    # 1. Hindi aliases (exact substring of the word itself — for Hindi tokens)
    for alias, canonical in _STATE_ALIASES.items():
        if alias.lower() == low:
            return canonical

    # 2. Exact STATE_MAP key — full word match
    found = STATE_MAP.get(low)
    if found:
        return found

    # 3. Multi-word keys (e.g. "uttar pradesh") won't match single words — skip
    # 4. For longer words (≥5 chars), check if a long-key is a PREFIX/CONTAINED
    if len(low) >= 5:
        for key, val in STATE_MAP.items():
            if len(key) >= 4 and (low.startswith(key) or key.startswith(low[:4])):
                return val

    # 5. rapidfuzz — handles typos like "rajsthan"→Rajasthan, "jharkand"→Jharkhand
    if _FUZZY and len(low) >= 4:
        match, score, _ = fuzz_process.extractOne(
            low, _ALL_STATES,
            scorer=fuzz.WRatio,
        )
        if score >= 82:
            return match

    return None


def rule_parse_profile(text: str) -> dict | None:
    """
    Pure open-source profile parser: regex + rapidfuzz, zero LLM.
    Returns profile dict if ≥2 fields found, else None.
    """
    low = text.lower()
    tokens = set(re.findall(r"[a-zA-Zऀ-ॿ]+", low))

    # ── Age ──────────────────────────────────────────────────────────────────
    age = None
    for m in _RE_AGE.finditer(text, re.IGNORECASE):
        val = int(m.group(1) or m.group(2))
        if 1 <= val <= 120:
            age = val
            break

    # ── Gender ───────────────────────────────────────────────────────────────
    gender = None
    if tokens & _GENDER_FEMALE:
        gender = "female"
    elif tokens & _GENDER_MALE:
        gender = "male"
    # widow / widoe / vidhwa typo variants → implies female
    if re.search(r"\bwid\w{1,4}\b|विधवा|vidhwa|bidhwa", low):
        gender = "female"

    # ── State ─────────────────────────────────────────────────────────────────
    state = None
    words = re.split(r"[\s,।;/]+", low)
    # First pass: skip very short tokens (≤3 chars) and common English words
    _SKIP = {"the", "and", "for", "old", "are", "was", "has", "mai", "hai",
             "hoo", "hun", "hun", "mera", "mere", "meri", "ka", "ki", "ke",
             "se", "me", "ko", "ne", "hi", "to", "bhi", "aur", "kya", "ek",
             "old", "man", "age", "girl", "boy", "she", "her", "his", "sc",
             "st", "obc", "ews", "bpl", "am", "an", "a", "i"}
    for i in range(len(words)):
        w = words[i]
        if w in _SKIP or (len(w) <= 2 and w not in STATE_MAP):
            continue
        s = _fuzzy_state(w)
        if s:
            state = s
            break
        # Try two-word combo for "uttar pradesh", "west bengal" etc.
        if i + 1 < len(words):
            two = f"{words[i]} {words[i+1]}"
            found = STATE_MAP.get(two)
            if found:
                state = found
                break

    # ── Caste (word-boundary patterns to avoid substring false matches) ──────
    caste = None
    for cat, pat in _CASTE_RE.items():
        if pat.search(text):
            caste = cat
            break

    # ── Income ───────────────────────────────────────────────────────────────
    income = None
    m = _RE_INCOME_LAKH.search(text)
    if m:
        income = int(float(m.group(1)) * 100000)
    else:
        m = _RE_INCOME_HAZAR.search(text)
        if m:
            income = int(float(m.group(1)) * 1000)
        else:
            m = _RE_INCOME_BARE.search(text)
            if m:
                income = int(m.group(1))

    # ── Flags (regex with word boundaries to avoid substring false matches) ──
    flags = []
    for flag, pat in _FLAG_RE.items():
        if pat.search(text):
            flags.append(flag)

    # ── Bare-number age fallback (last resort when other fields confirm profile) ──
    if age is None:
        other_signals = sum([gender is not None, state is not None,
                             caste is not None, income is not None, len(flags) > 0])
        if other_signals >= 1:
            for m in _RE_BARE_NUM.finditer(text):
                val = int(m.group(1))
                if 5 <= val <= 100:
                    age = val
                    break

    # ── Validity check ────────────────────────────────────────────────────────
    fields_found = sum([
        age is not None,
        gender is not None,
        state is not None,
        caste is not None,
        income is not None,
        len(flags) > 0,
    ])
    if fields_found < 2:
        return None

    return {
        "age":    age,
        "gender": gender or "",
        "state":  state or "All",
        "caste":  caste or "",
        "income": income or 0,
        "flags":  flags,
    }


# ── Cached LLM system prompts (built once at startup, reused every call) ─────

_PROFILE_SYSTEM_PROMPT = """You extract a user's personal profile from free-text messages in Hindi, English, or Hinglish (mixed).
The profile is used to match Indian government scheme eligibility.

OUTPUT: Return ONLY a single JSON object — no explanation, no markdown, no extra text.
{"age":<int|null>,"gender":<"male"|"female"|"other"|null>,"state":<full Indian state name in English|null>,"caste":<"SC"|"ST"|"OBC"|"EWS"|"General"|null>,"income":<annual INR int|null>,"flags":<[] or subset of ["widow","disability","minority","bpl","pregnant"]>}

RULES:
1. EXPLICIT caste always wins — if user says "SC tribe", caste="SC" (not ST).
2. Typo-tolerant states: "rajsthan"→"Rajasthan", "jharkand"→"Jharkhand", "maharastra"→"Maharashtra", "UP"→"Uttar Pradesh", "MP"→"Madhya Pradesh", "CG"→"Chhattisgarh".
3. Widow variants: "vidwa", "vidhwa", "widoe", "widow", "विधवा" → add "widow" to flags AND set gender="female".
4. Income: "1.5 lakh"→150000, "50k"→50000, "2 lakh"→200000, "80 hazar"→80000.
5. Age: accept "35 saal", "40 साल", "age 50", "35 year old", "mai 45 ka hoon", bare numbers near caste/state context.
6. If the message is NOT a profile (e.g. asking a question like "घर बनाने के लिए पैसे चाहिए"), return ALL nulls and empty flags [].

EXAMPLES:
"मैं 45 साल की विधवा हूं UP से BPL है" → {"age":45,"gender":"female","state":"Uttar Pradesh","caste":null,"income":null,"flags":["widow","bpl"]}
"35 year old SC Bihar farmer" → {"age":35,"gender":"male","state":"Bihar","caste":"SC","income":null,"flags":[]}
"mai 40 saal rajsthan OBC" → {"age":40,"gender":null,"state":"Rajasthan","caste":"OBC","income":null,"flags":[]}
"widoe 50 maharastra" → {"age":50,"gender":"female","state":"Maharashtra","caste":null,"income":null,"flags":["widow"]}
"SC tribe widoe 33 jharkand bpl" → {"age":33,"gender":"female","state":"Jharkhand","caste":"SC","income":null,"flags":["widow","bpl"]}
"disability pension 60 saal kerala" → {"age":60,"gender":null,"state":"Kerala","caste":null,"income":null,"flags":["disability"]}
"obc 45 haryana income 1.5 lakh" → {"age":45,"gender":null,"state":"Haryana","caste":"OBC","income":150000,"flags":[]}
"EWS 62 saal delhi bpl card hai" → {"age":62,"gender":null,"state":"Delhi","caste":"EWS","income":null,"flags":["bpl"]}
"pregnant woman 28 years assam ST" → {"age":28,"gender":"female","state":"Assam","caste":"ST","income":null,"flags":["pregnant"]}
"घर बनाने के लिए पैसे चाहिए" → {"age":null,"gender":null,"state":null,"caste":null,"income":null,"flags":[]}"""

_SEARCH_KEYWORDS_PROMPT = """Convert an Indian user's query about government schemes into 2-3 English search keywords.
Return ONLY the keywords as a short phrase — no explanation, no punctuation.
Examples:
"घर बनाने के लिए पैसे" → "housing construction"
"बेटी की पढ़ाई के लिए" → "girl education scholarship"
"कृषि ऋण माफी" → "farmer loan waiver"
"बुजुर्ग पेंशन" → "old age pension"
"दिव्यांग भत्ता" → "disability allowance"
"विधवा पेंशन" → "widow pension"
Return ONLY 2-4 keywords."""

# Follow-up Q&A prompts cached per language — avoids rebuilding the string on every call
_FOLLOWUP_SYSTEM_PROMPTS: dict[str, str] = {
    "hi": """आप Saavi हैं — Aarambha Haq के सहायक, भारत का मुफ्त सरकारी योजना खोज इंजन।
नीचे दी गई सरकारी योजनाओं के बारे में यूजर के सवाल का 2-4 वाक्यों में जवाब दें।
हिंदी (देवनागरी) में जवाब दें। केवल दी गई जानकारी से जवाब दें — अनुमान न लगाएं।""",

    "en": """You are Saavi, assistant for Aarambha Haq — India's free government scheme finder.
Answer the user's follow-up question in 2-4 sentences based ONLY on the scheme data provided.
Respond in English. If the answer isn't in the data, say so simply.""",

    "mr": """तुम्ही Saavi आहात — Aarambha Haq चे सहाय्यक, भारताचे मोफत सरकारी योजना शोध इंजिन।
खालील सरकारी योजनांबद्दल वापरकर्त्याच्या प्रश्नाचे 2-4 वाक्यांत उत्तर द्या।
मराठीत उत्तर द्या। फक्त दिलेल्या माहितीवरून उत्तर द्या।""",

    "bn": """আপনি Saavi — Aarambha Haq-এর সহকারী, ভারতের বিনামূল্যে সরকারি প্রকল্প অনুসন্ধান ইঞ্জিন।
নীচের সরকারি প্রকল্পগুলি সম্পর্কে ব্যবহারকারীর প্রশ্নের 2-4 বাক্যে উত্তর দিন।
বাংলায় উত্তর দিন। শুধুমাত্র প্রদত্ত তথ্য থেকে উত্তর দিন।""",

    "te": """మీరు Saavi — Aarambha Haq సహాయకుడు, భారతదేశం యొక్క ఉచిత ప్రభుత్వ పథకాల శోధన సేవ.
దిగువ పథకాలపై వినియోగదారు ప్రశ్నకు 2-4 వాక్యాలలో సమాధానం ఇవ్వండి.
తెలుగులో సమాధానం ఇవ్వండి. అందించిన సమాచారం ఆధారంగా మాత్రమే జవాబు ఇవ్వండి।""",

    "ta": """நீங்கள் Saavi — Aarambha Haq உதவியாளர், இந்தியாவின் இலவச அரசாங்க திட்டங்கள் தேடல் சேவை.
கீழே உள்ள திட்டங்கள் பற்றிய பயனரின் கேள்விக்கு 2-4 வாக்கியங்களில் பதிலளிக்கவும்.
தமிழில் பதிலளிக்கவும். வழங்கப்பட்ட தகவல்களின் அடிப்படையில் மட்டுமே பதிலளிக்கவும்।""",

    "gu": """તમે Saavi છો — Aarambha Haq ના સહાયક, ભારતની મફત સરકારી યોજના શોધ સેવા.
નીચેની સરકારી યોજનાઓ વિશે વપરાશકર્તાના પ્રશ્નનો 2-4 વાક્યોમાં જવાબ આપો.
ગુજરાતીમાં જવાબ આપો। ફક્ત આપેલ માહિતી પરથી જ જવાબ આપો।""",

    "kn": """ನೀವು Saavi — Aarambha Haq ಸಹಾಯಕ, ಭಾರತದ ಉಚಿತ ಸರ್ಕಾರಿ ಯೋಜನೆ ಹುಡುಕಾಟ ಸೇವೆ.
ಕೆಳಗಿನ ಯೋಜನೆಗಳ ಕುರಿತು ಬಳಕೆದಾರರ ಪ್ರಶ್ನೆಗೆ 2-4 ವಾಕ್ಯಗಳಲ್ಲಿ ಉತ್ತರಿಸಿ.
ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ. ನೀಡಿದ ಮಾಹಿತಿಯ ಆಧಾರದ ಮೇಲೆ ಮಾತ್ರ ಉತ್ತರಿಸಿ।""",

    "pa": """ਤੁਸੀਂ Saavi ਹੋ — Aarambha Haq ਦੇ ਸਹਾਇਕ, ਭਾਰਤ ਦੀ ਮੁਫ਼ਤ ਸਰਕਾਰੀ ਯੋਜਨਾ ਖੋਜ ਸੇਵਾ।
ਹੇਠਾਂ ਦਿੱਤੀਆਂ ਯੋਜਨਾਵਾਂ ਬਾਰੇ ਉਪਭੋਗਤਾ ਦੇ ਸਵਾਲ ਦਾ 2-4 ਵਾਕਾਂ ਵਿੱਚ ਜਵਾਬ ਦਿਓ।
ਪੰਜਾਬੀ ਵਿੱਚ ਜਵਾਬ ਦਿਓ। ਸਿਰਫ਼ ਦਿੱਤੀ ਗਈ ਜਾਣਕਾਰੀ ਤੋਂ ਜਵਾਬ ਦਿਓ।""",

    "ml": """നിങ്ങൾ Saavi ആണ് — Aarambha Haq സഹായി, ഇന്ത്യയുടെ സൗജന്യ സർക്കാർ പദ്ധതി തിരയൽ സേവനം.
താഴെ നൽകിയ പദ്ധതികളെക്കുറിച്ചുള്ള ഉപയോക്താവിന്റെ ചോദ്യത്തിന് 2-4 വാക്യങ്ങളിൽ ഉത്തരം നൽകുക.
മലയാളത്തിൽ ഉത്തരം നൽകുക. നൽകിയ വിവരങ്ങളുടെ അടിസ്ഥാനത്തിൽ മാത്രം ഉത്തരം നൽകുക।""",
}


# ── Smart NLP helpers ────────────────────────────────────────────────────────

def smart_parse_profile(text: str) -> dict | None:
    """
    Parse free-text user message into a profile dict.
    Strategy: rule_parse_profile() first (free, instant), Groq LLM fallback if < 2 fields.
    e.g. "मैं 45 साल की विधवा हूं UP से BPL है" →
         {age:45, gender:"female", state:"Uttar Pradesh", flags:["widow","bpl"]}
    Returns None if message doesn't look like a profile description.
    """
    if len(text.split()) < 3:
        return None

    # Fast rule-based pass — no API call
    rule_result = rule_parse_profile(text)
    if rule_result:
        return rule_result

    # Groq LLM fallback for ambiguous/complex sentences
    if not GROQ_KEY:
        return None

    profile_hints = [
        "साल", "year", "उम्र", "age", "हूं", "हूँ", "हैं", "am ", "i am",
        "विधवा", "widow", "BPL", "SC", "ST", "OBC", "महिला", "female",
        "राज्य", "state", "से हूं", "रहती", "रहता", "income", "आय",
    ]
    if not any(h.lower() in text.lower() for h in profile_hints):
        return None

    raw = llm_call(
        prompt=text,
        system=_PROFILE_SYSTEM_PROMPT,
        json_mode=True,
    )
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
        # Must have at least one real field to be valid
        if not any(parsed.get(k) for k in ("age", "gender", "state", "caste", "income")) \
                and not parsed.get("flags"):
            return None
        # Clean up
        profile = {
            "age":    int(parsed["age"]) if parsed.get("age") else None,
            "gender": parsed.get("gender") or "",
            "state":  parsed.get("state") or "All",
            "caste":  parsed.get("caste") or "",
            "income": int(parsed["income"]) if parsed.get("income") else 0,
            "flags":  parsed.get("flags") or [],
        }
        return profile
    except Exception:
        return None


def smart_search_keywords(query: str) -> str:
    """
    Convert a natural language query into search keywords.
    e.g. "घर बनाने के लिए पैसे चाहिए" → "housing construction scheme"
    Falls back to original query if Groq fails.
    """
    raw = llm_call(
        prompt=f"User query: {query}",
        system=_SEARCH_KEYWORDS_PROMPT,
    )
    return raw.strip() if raw and len(raw.strip()) < 60 else query


def smart_followup(question: str, schemes: list[dict], lang: str) -> str | None:
    """
    Answer a follow-up question about the shown schemes using Groq LLM.
    e.g. "इसमें कितना पैसा मिलेगा?" given scheme list → clear Hindi answer.
    """
    if not schemes:
        return None
    # Build compact scheme summary for context
    context_lines = []
    for s in schemes[:5]:
        amt = f"₹{s['benefit_amount_inr']:,}" if s.get("benefit_amount_inr") else s.get("benefit_amount_description","")
        context_lines.append(
            f"- {s['name']}: {s.get('description','')[:100]} | Benefit: {amt}"
        )
    context = "\n".join(context_lines)

    system = _FOLLOWUP_SYSTEM_PROMPTS.get(lang, _FOLLOWUP_SYSTEM_PROMPTS["en"])
    raw = llm_call(
        prompt=f"Schemes:\n{context}\n\nUser question: {question}",
        system=system,
    )
    return raw.strip() if raw else None


# ── User state via API (no direct DB — avoids peer auth issues) ───────────────
def get_user(chat_id: int) -> dict:
    try:
        r = requests.get(f"{API_BASE}/api/bot/user/{chat_id}", timeout=5)
        return r.json() if r.ok else {}
    except Exception:
        return {}


def save_user(chat_id: int, **kwargs):
    try:
        requests.post(f"{API_BASE}/api/bot/user/{chat_id}", json=kwargs, timeout=5)
    except Exception:
        pass


def get_lang(chat_id: int) -> str:
    u = get_user(chat_id)
    return u.get("lang", "hi")


def t(chat_id: int, key: str, **fmt) -> str:
    lang = get_lang(chat_id)
    ui = UI.get(lang, UI["hi"])
    text = ui.get(key, UI["hi"].get(key, key))
    return text.format(**fmt) if fmt else text


# ── API helpers ───────────────────────────────────────────────────────────────
def api_check(profile: dict) -> list[dict]:
    try:
        params = {
            "gender":         profile.get("gender", ""),
            "age":            profile.get("age", 30),
            "state":          profile.get("state", "All"),
            "income":         profile.get("income", 0),
            "caste":          profile.get("caste", ""),
            "has_disability": 1 if "disability" in profile.get("flags", []) else 0,
            "is_minority":    1 if "minority"   in profile.get("flags", []) else 0,
            "has_bpl":        1 if "bpl"        in profile.get("flags", []) else 0,
        }
        r = requests.get(f"{API_BASE}/api/check/results", params=params, timeout=10)
        return r.json().get("schemes", []) if r.ok else []
    except Exception:
        return []


def api_search(q: str, lang: str = "hi") -> list[dict]:
    try:
        r = requests.get(
            f"{API_BASE}/api/schemes",
            params={"q": q, "size": 8, "page": 1},
            timeout=10,
        )
        return r.json().get("schemes", []) if r.ok else []
    except Exception:
        return []


def api_rights(category: str = "") -> list[dict]:
    try:
        params = {"category": category} if category else {}
        r = requests.get(f"{API_BASE}/api/rights", params=params, timeout=10)
        return r.json().get("articles", []) if r.ok else []
    except Exception:
        return []


# ── Keyboards ────────────────────────────────────────────────────────────────
def menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    ui = UI.get(lang, UI["hi"])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(ui["check_lbl"],  callback_data="menu:check")],
        [InlineKeyboardButton(ui["search_lbl"], callback_data="menu:search")],
        [InlineKeyboardButton(ui["rights_lbl"], callback_data="menu:rights")],
        [InlineKeyboardButton(ui["lang_lbl"],   callback_data="menu:lang")],
    ])


def lang_keyboard() -> InlineKeyboardMarkup:
    rows = []
    row = []
    for code, label in LANG_OPTIONS:
        row.append(InlineKeyboardButton(label, callback_data=f"lang:{code}"))
        if len(row) == 3:
            rows.append(row); row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(rows)


def gender_keyboard(lang: str) -> InlineKeyboardMarkup:
    ui = UI.get(lang, UI["hi"])
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(ui["female"], callback_data="gender:female"),
        InlineKeyboardButton(ui["male"],   callback_data="gender:male"),
        InlineKeyboardButton(ui["other"],  callback_data="gender:other"),
    ]])


def caste_keyboard(lang: str) -> InlineKeyboardMarkup:
    opts = CASTE_OPTIONS.get(lang, CASTE_OPTIONS["hi"])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(label, callback_data=f"caste:{val}")]
        for label, val in opts
    ])


def income_keyboard(lang: str) -> InlineKeyboardMarkup:
    opts = INCOME_OPTIONS.get(lang, INCOME_OPTIONS["hi"])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(label, callback_data=f"income:{val}")]
        for label, val in opts
    ])


def flags_keyboard(lang: str, selected: list[str]) -> InlineKeyboardMarkup:
    opts = FLAG_OPTIONS.get(lang, FLAG_OPTIONS["hi"])
    rows = []
    for label, val in opts:
        check = "✅ " if val in selected else "☐ "
        rows.append([InlineKeyboardButton(check + label, callback_data=f"flag:{val}")])
    rows.append([InlineKeyboardButton(
        UI.get(lang, UI["hi"])["done_flags"], callback_data="flag:done"
    )])
    return InlineKeyboardMarkup(rows)


def rights_keyboard(lang: str) -> InlineKeyboardMarkup:
    opts = RIGHTS_CATEGORIES.get(lang, RIGHTS_CATEGORIES["hi"])
    rows = [[InlineKeyboardButton(label, callback_data=f"rights:{slug}")] for slug, label in opts]
    rows.append([InlineKeyboardButton("⬅️ Menu", callback_data="menu:back")])
    return InlineKeyboardMarkup(rows)


# ── Scheme formatter ──────────────────────────────────────────────────────────
def fmt_scheme(s: dict, idx: int) -> str:
    name  = s.get("name", "")[:60]
    level = "🏛" if s.get("level") == "Central" else "🗺"
    state = f" • {s['state']}" if s.get("state") and s["state"] != "All" else ""
    btype = s.get("benefit_type") or ""
    bamt  = s.get("benefit_amount_inr")
    benefit = ""
    if bamt:
        if bamt >= 100000:
            benefit = f"\n  💰 ₹{bamt/100000:.1f} लाख"
        else:
            benefit = f"\n  💰 ₹{bamt:,}"
    elif s.get("benefit_amount_description"):
        benefit = f"\n  💰 {s['benefit_amount_description'][:50]}"

    return f"{idx}. {level} *{name}*{state}{benefit}"


def scheme_apply_buttons(schemes: list[dict], offset: int = 0) -> InlineKeyboardMarkup:
    rows = []
    for i, s in enumerate(schemes):
        url = s.get("apply_url", "")
        if url:
            rows.append([InlineKeyboardButton(
                f"📋 {i+1+offset}. आवेदन करें",
                url=url,
            )])
    return InlineKeyboardMarkup(rows) if rows else None


# ── Handlers ─────────────────────────────────────────────────────────────────
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id    = update.effective_chat.id
    first_name = update.effective_user.first_name or ""
    username   = update.effective_user.username or ""
    save_user(chat_id, step="idle", first_name=first_name, username=username)

    await update.message.reply_text(
        UI["hi"]["welcome"],
        reply_markup=lang_keyboard(),
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang    = get_lang(chat_id)
    save_user(chat_id, step="idle")
    await update.message.reply_text(
        t(chat_id, "menu"),
        reply_markup=menu_keyboard(lang),
    )


async def cmd_search(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    save_user(chat_id, step="search")
    await update.message.reply_text(t(chat_id, "search_prompt"))


async def cmd_check(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    save_user(chat_id, step="ask_state", profile={})
    await update.message.reply_text(t(chat_id, "ask_state"))


async def cmd_haq(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang    = get_lang(chat_id)
    await update.message.reply_text(
        t(chat_id, "rights_hdr"),
        reply_markup=rights_keyboard(lang),
        parse_mode=ParseMode.MARKDOWN,
    )


# ── Callback router ───────────────────────────────────────────────────────────
async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query   = update.callback_query
    chat_id = query.message.chat.id
    data    = query.data
    lang    = get_lang(chat_id)

    await query.answer()

    # ── language selection ────────────────────────────────────────────────────
    if data.startswith("lang:"):
        new_lang = data.split(":")[1]
        save_user(chat_id, lang=new_lang, step="idle")
        lang = new_lang
        await query.edit_message_text(
            UI.get(lang, UI["hi"])["menu"],
            reply_markup=menu_keyboard(lang),
        )

    # ── main menu ─────────────────────────────────────────────────────────────
    elif data == "menu:lang":
        await query.edit_message_text(
            UI.get(lang, UI["hi"])["welcome"],
            reply_markup=lang_keyboard(),
            parse_mode=ParseMode.MARKDOWN,
        )

    elif data == "menu:check":
        save_user(chat_id, step="ask_state", profile={})
        await query.edit_message_text(t(chat_id, "ask_state"))

    elif data == "menu:search":
        save_user(chat_id, step="search")
        await query.edit_message_text(t(chat_id, "search_prompt"))

    elif data == "menu:rights" or data == "menu:back":
        await query.edit_message_text(
            t(chat_id, "rights_hdr"),
            reply_markup=rights_keyboard(lang),
            parse_mode=ParseMode.MARKDOWN,
        )

    # ── wizard steps via inline ───────────────────────────────────────────────
    elif data.startswith("gender:"):
        gender = data.split(":")[1]
        user   = get_user(chat_id)
        profile = user.get("profile") or {}
        if isinstance(profile, str):
            profile = json.loads(profile)
        profile["gender"] = gender
        save_user(chat_id, step="ask_caste", profile=json.dumps(profile))
        await query.edit_message_text(
            t(chat_id, "ask_caste"),
            reply_markup=caste_keyboard(lang),
        )

    elif data.startswith("caste:"):
        caste  = data.split(":")[1]
        user   = get_user(chat_id)
        profile = user.get("profile") or {}
        if isinstance(profile, str):
            profile = json.loads(profile)
        profile["caste"] = caste
        save_user(chat_id, step="ask_income", profile=json.dumps(profile))
        await query.edit_message_text(
            t(chat_id, "ask_income"),
            reply_markup=income_keyboard(lang),
        )

    elif data.startswith("income:"):
        income = int(data.split(":")[1])
        user   = get_user(chat_id)
        profile = user.get("profile") or {}
        if isinstance(profile, str):
            profile = json.loads(profile)
        profile["income"] = income
        profile.setdefault("flags", [])
        save_user(chat_id, step="ask_flags", profile=json.dumps(profile))
        await query.edit_message_text(
            t(chat_id, "ask_flags"),
            reply_markup=flags_keyboard(lang, profile["flags"]),
        )

    elif data.startswith("flag:"):
        flag   = data.split(":")[1]
        user   = get_user(chat_id)
        profile = user.get("profile") or {}
        if isinstance(profile, str):
            profile = json.loads(profile)
        flags  = profile.setdefault("flags", [])

        if flag == "done":
            # Run the eligibility check
            save_user(chat_id, step="idle")
            await query.edit_message_text(t(chat_id, "searching"))
            schemes = api_check(profile)
            if not schemes:
                await query.edit_message_text(
                    t(chat_id, "no_results"),
                    reply_markup=menu_keyboard(lang),
                )
            else:
                lines = [t(chat_id, "results_hdr", n=len(schemes))]
                shown = schemes[:7]
                for i, s in enumerate(shown, 1):
                    lines.append(fmt_scheme(s, i))
                text = "\n".join(lines)
                kb   = scheme_apply_buttons(shown)
                if kb:
                    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN)
                    await query.message.reply_text(
                        t(chat_id, "website_link"),
                        reply_markup=kb,
                    )
                else:
                    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN)
                # Show menu again
                await query.message.reply_text(
                    t(chat_id, "menu"),
                    reply_markup=menu_keyboard(lang),
                )
        else:
            # Toggle flag
            if flag in flags:
                flags.remove(flag)
            else:
                flags.append(flag)
            profile["flags"] = flags
            save_user(chat_id, profile=json.dumps(profile))
            await query.edit_message_text(
                t(chat_id, "ask_flags"),
                reply_markup=flags_keyboard(lang, flags),
            )

    # ── rights ────────────────────────────────────────────────────────────────
    elif data.startswith("rights:"):
        category = data.split(":")[1]
        articles = api_rights(category)
        if not articles:
            await query.edit_message_text("कोई अधिकार नहीं मिला।")
            return

        cat_labels = dict(
            (s, l) for s, l in RIGHTS_CATEGORIES.get(lang, RIGHTS_CATEGORIES["hi"])
        )
        header = f"*{cat_labels.get(category, 'अधिकार')}*\n\n"
        lines  = []
        for a in articles[:6]:
            lines.append(f"• *{a['title_hi']}*\n  {a['summary_hi'][:120]}...\n")
        text = header + "\n".join(lines) + "\n🌐 haq.aarambhax.in/hi/haq"

        await query.edit_message_text(
            text,
            reply_markup=rights_keyboard(lang),
            parse_mode=ParseMode.MARKDOWN,
        )


# ── Text message handler (state-driven + smart NLP) ──────────────────────────
async def on_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text    = update.message.text.strip()
    lang    = get_lang(chat_id)
    user    = get_user(chat_id)
    step    = user.get("step", "idle")

    # ── State machine ─────────────────────────────────────────────────────────
    if step == "ask_state":
        profile = {}
        profile["state"] = _normalize_state(text)
        save_user(chat_id, step="ask_age", profile=json.dumps(profile))
        await update.message.reply_text(t(chat_id, "ask_age"))

    elif step == "ask_age":
        if not re.match(r"^\d{1,3}$", text) or not (1 <= int(text) <= 120):
            await update.message.reply_text(t(chat_id, "invalid_age"))
            return
        profile = user.get("profile") or {}
        if isinstance(profile, str):
            profile = json.loads(profile)
        profile["age"] = int(text)
        save_user(chat_id, step="ask_gender", profile=json.dumps(profile))
        await update.message.reply_text(
            t(chat_id, "ask_gender"),
            reply_markup=gender_keyboard(lang),
        )

    elif step == "search":
        save_user(chat_id, step="idle")
        # Smart: if natural language, extract keywords first
        query = text
        if len(text.split()) > 3 and GROQ_KEY:
            await update.message.reply_text("🔍 समझ रहे हैं..." if lang == "hi" else "🔍 Analyzing...")
            better = smart_search_keywords(text)
            if better and better != text:
                query = better

        schemes = api_search(query, lang)
        if not schemes and query != text:
            schemes = api_search(text, lang)  # fallback to original

        if not schemes:
            await update.message.reply_text(
                f"'{text}' के लिए कोई योजना नहीं मिली।\nदूसरे शब्द आज़माएं।"
                if lang == "hi" else
                f"No schemes found for '{text}'. Try different keywords."
            )
            return

        lines = [f"🔍 *{len(schemes)} योजनाएं मिलीं*\n" if lang == "hi" else f"🔍 *{len(schemes)} schemes found*\n"]
        shown = schemes[:6]
        for i, s in enumerate(shown, 1):
            lines.append(fmt_scheme(s, i))

        # Save results for follow-up Q&A
        save_user(chat_id, results=json.dumps(shown))

        kb = scheme_apply_buttons(shown)
        await update.message.reply_text(
            "\n".join(lines),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=kb or None,
        )
        # Prompt for follow-up
        followup_hint = (
            "💬 कोई सवाल पूछें — जैसे 'इसमें कितना मिलेगा?' या 'कैसे apply करें?'"
            if lang == "hi" else
            "💬 Ask a follow-up — e.g. 'How much money?' or 'How to apply?'"
        )
        await update.message.reply_text(
            followup_hint,
            reply_markup=menu_keyboard(lang),
        )

    elif step == "awaiting_followup":
        # User is asking a follow-up about last shown schemes
        results = user.get("results")
        schemes = json.loads(results) if results else []
        save_user(chat_id, step="idle")

        thinking_msg = await update.message.reply_text(
            "🤔 सोच रहे हैं..." if lang == "hi" else "🤔 Thinking..."
        )
        answer = smart_followup(text, schemes, lang) if GROQ_KEY else None
        await thinking_msg.delete()

        if answer:
            await update.message.reply_text(answer, reply_markup=menu_keyboard(lang))
        else:
            await update.message.reply_text(
                "माफ़ करें, अभी जवाब नहीं दे पा रहे। वेबसाइट पर देखें: haq.aarambhax.in"
                if lang == "hi" else
                "Sorry, can't answer right now. Visit: haq.aarambhax.in",
                reply_markup=menu_keyboard(lang),
            )

    elif step == "idle":
        # Smart mode: try to parse free-text profile (rule-based first, Groq fallback)
        if len(text.split()) >= 3:
            thinking = await update.message.reply_text(
                "🤖 समझ रहे हैं..." if lang == "hi" else "🤖 Understanding..."
            )
            profile = smart_parse_profile(text)
            await thinking.delete()

            if profile:
                # Confirm what was understood
                understood_lines = []
                if profile.get("age"):
                    understood_lines.append(f"• उम्र: {profile['age']} साल" if lang == "hi" else f"• Age: {profile['age']}")
                if profile.get("gender"):
                    g = {"female":"महिला","male":"पुरुष","other":"अन्य"}.get(profile["gender"], profile["gender"])
                    understood_lines.append(f"• लिंग: {g}" if lang == "hi" else f"• Gender: {profile['gender']}")
                if profile.get("state") and profile["state"] != "All":
                    understood_lines.append(f"• राज्य: {profile['state']}" if lang == "hi" else f"• State: {profile['state']}")
                if profile.get("caste"):
                    understood_lines.append(f"• वर्ग: {profile['caste']}")
                if profile.get("income"):
                    understood_lines.append(f"• आय: ₹{profile['income']:,}/साल" if lang == "hi" else f"• Income: ₹{profile['income']:,}/yr")
                if profile.get("flags"):
                    flags_hi = {"widow":"विधवा","disability":"दिव्यांग","minority":"अल्पसंख्यक","bpl":"BPL","pregnant":"गर्भवती"}
                    f_labels = [flags_hi.get(f,f) if lang=="hi" else f for f in profile["flags"]]
                    understood_lines.append(f"• अन्य: {', '.join(f_labels)}" if lang == "hi" else f"• Flags: {', '.join(f_labels)}")

                confirm_text = (
                    "✅ *समझा! आपकी जानकारी:*\n" + "\n".join(understood_lines) + "\n\n🔍 योजनाएं खोज रहे हैं..."
                    if lang == "hi" else
                    "✅ *Got it! Your profile:*\n" + "\n".join(understood_lines) + "\n\n🔍 Finding schemes..."
                )
                await update.message.reply_text(confirm_text, parse_mode=ParseMode.MARKDOWN)

                schemes = api_check(profile)
                save_user(chat_id, profile=json.dumps(profile), results=json.dumps(schemes[:7]))

                if not schemes:
                    await update.message.reply_text(
                        t(chat_id, "no_results"), reply_markup=menu_keyboard(lang)
                    )
                else:
                    lines = [t(chat_id, "results_hdr", n=len(schemes))]
                    shown = schemes[:7]
                    for i, s in enumerate(shown, 1):
                        lines.append(fmt_scheme(s, i))
                    kb = scheme_apply_buttons(shown)
                    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)
                    if kb:
                        await update.message.reply_text(t(chat_id, "website_link"), reply_markup=kb)
                    # Enable follow-up mode
                    save_user(chat_id, step="awaiting_followup")
                    await update.message.reply_text(
                        "💬 कोई सवाल पूछें — 'कितना मिलेगा?' 'कैसे apply करें?' 'कौन सी सबसे अच्छी?'"
                        if lang == "hi" else
                        "💬 Ask anything — 'How much?' 'How to apply?' 'Which is best?'",
                        reply_markup=menu_keyboard(lang),
                    )
            else:
                # Not a profile → show menu
                await update.message.reply_text(
                    t(chat_id, "menu"), reply_markup=menu_keyboard(lang)
                )
        else:
            await update.message.reply_text(
                t(chat_id, "menu"), reply_markup=menu_keyboard(lang)
            )

    else:
        # Unknown state → show menu
        await update.message.reply_text(
            t(chat_id, "menu"), reply_markup=menu_keyboard(lang),
        )


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if not BOT_TOKEN:
        print("❌ Set TELEGRAM_BOT_TOKEN env var first.")
        print("   Get it from @BotFather on Telegram.")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("menu",   cmd_menu))
    app.add_handler(CommandHandler("check",  cmd_check))
    app.add_handler(CommandHandler("search", cmd_search))
    app.add_handler(CommandHandler("haq",    cmd_haq))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    print("🤖 Aarambha Haq bot started. Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
