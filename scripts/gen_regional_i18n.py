#!/usr/bin/env python3
"""
Generate UI i18n strings + state names for Rajasthani, Bhojpuri, Chhattisgarhi.
Single Gemini call for all 3 languages at once.
"""

from __future__ import annotations
import json, time, urllib.request, urllib.error
from pathlib import Path

FREE_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL    = "gemini-3.1-flash-lite"
URL      = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"

I18N_DIR = Path(__file__).parent.parent / "web" / "static" / "i18n"

# ── Reference: all UI keys from hi.json ───────────────────────────────────
HI_KEYS = json.loads((I18N_DIR / "hi.json").read_text())
# Remove _meta — that's not translatable
KEYS = {k: v for k, v in HI_KEYS.items() if k != "_meta"}

# ── Reference: all states from states.json ────────────────────────────────
STATES_JSON = json.loads((I18N_DIR / "states.json").read_text())
ALL_STATES  = list(STATES_JSON["hi"].keys())   # 36 states in English

LANGS = {
    "raj": {
        "name": "Rajasthani",
        "native": "राजस्थानी",
        "notes": (
            "Rajasthani dialect — Devanagari script. "
            "Use: आपां=हम, थारा=आपका, कोनी=नहीं, घणो/घणी=बहुत, राम-राम सा=नमस्ते, "
            "म्हारो=हमारा, हां जी=हाँ, सा=respectful suffix. "
            "Keep English numbers and acronyms (BPL, SC, ST, OBC, SHG, EWS, CSC). "
            "UI strings should feel warm and colloquial."
        ),
    },
    "bho": {
        "name": "Bhojpuri",
        "native": "भोजपुरी",
        "notes": (
            "Bhojpuri dialect — Devanagari script. "
            "Use: रउवा=आप, हमार=हमारा, बा=है, बाड़न=हैं, खातिर=के लिए, "
            "भइया=भाई, होखे=होता है, मिली=मिलेगा, देवे=देता है, बहुते=बहुत. "
            "Keep English numbers and acronyms. UI strings should feel friendly and conversational."
        ),
    },
    "hne": {
        "name": "Chhattisgarhi",
        "native": "छत्तीसगढ़ी",
        "notes": (
            "Chhattisgarhi dialect — Devanagari script. "
            "Use: संगवारी=दोस्त, हावय=है, थे=आप, मन=plural suffix, "
            "जय जोहार=नमस्ते, कइसे=कैसे, बने=अच्छा, ले=से, करे=करता है. "
            "Keep English numbers and acronyms. UI strings should feel local and warm."
        ),
    },
}


def call_gemini(prompt: str) -> dict:
    payload = json.dumps({
        "model":    MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert translator of Indian regional dialects. Return ONLY valid JSON."},
            {"role": "user",   "content": prompt},
        ],
        "max_tokens":      65536,
        "response_format": {"type": "json_object"},
    }).encode()

    for attempt in range(3):
        try:
            req = urllib.request.Request(
                URL, data=payload,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {FREE_KEY}"},
            )
            with urllib.request.urlopen(req, timeout=120) as r:
                content = json.loads(r.read())["choices"][0]["message"]["content"]
                return json.loads(content)
        except urllib.error.HTTPError as e:
            print(f"  HTTP {e.code} attempt {attempt+1}: {e.read().decode()[:120]}")
            time.sleep(15 * (attempt + 1))
        except Exception as ex:
            print(f"  Error attempt {attempt+1}: {ex}")
            time.sleep(10)
    raise RuntimeError("Gemini call failed after 3 attempts")


def build_ui_prompt() -> str:
    lang_notes = "\n".join(f"- {code}: {info['notes']}" for code, info in LANGS.items())
    # Provide hi.json as reference for every key
    keys_list = "\n".join(f'  "{k}": "{v}"' for k, v in KEYS.items())

    return f"""Translate these Indian government portal UI strings into 3 regional dialects.

DIALECT INSTRUCTIONS:
{lang_notes}

REFERENCE (Hindi translations — translate the MEANING, not literally):
{{{keys_list}
}}

OUTPUT — return exactly this JSON structure:
{{
  "raj": {{
    "_meta": {{"code":"raj","name":"Rajasthani","native":"राजस्थानी","script":"Devanagari","dir":"ltr"}},
    "nav.check_eligibility": "<Rajasthani translation>",
    ... (ALL keys from reference, same key names)
  }},
  "bho": {{
    "_meta": {{"code":"bho","name":"Bhojpuri","native":"भोजपुरी","script":"Devanagari","dir":"ltr"}},
    ... (ALL keys)
  }},
  "hne": {{
    "_meta": {{"code":"hne","name":"Chhattisgarhi","native":"छत्तीसगढ़ी","script":"Devanagari","dir":"ltr"}},
    ... (ALL keys)
  }}
}}

Rules:
- Keep template placeholders: {{n}}, {{total}} — do NOT translate them
- Keep numbers, acronyms: BPL, SC, ST, OBC, SHG, EWS, CSC, Aadhaar, ₹
- Use authentic dialect vocabulary from the instructions
- Pure JSON only — no markdown or explanations"""


def build_states_prompt() -> str:
    lang_notes = "\n".join(f"- {code}: {info['notes']}" for code, info in LANGS.items())
    states_list = "\n".join(f"  {s}" for s in ALL_STATES)

    return f"""Translate these 36 Indian states/UTs names into 3 regional dialects.

DIALECT INSTRUCTIONS:
{lang_notes}

STATES TO TRANSLATE:
{states_list}

OUTPUT — return exactly this JSON:
{{
  "raj": {{
    "Andhra Pradesh": "<Rajasthani name>",
    "Arunachal Pradesh": "...",
    ... (all 36 states)
  }},
  "bho": {{...}},
  "hne": {{...}}
}}

Rules:
- Use Devanagari script for all 3 languages
- State names should sound natural in each dialect
- Keep well-known names close to Hindi (just with dialect pronunciation/script)
- Pure JSON only"""


def main():
    print("Generating UI strings for raj/bho/hne...")
    ui_data = call_gemini(build_ui_prompt())
    print(f"  Got keys: raj={len(ui_data.get('raj',{}))}, bho={len(ui_data.get('bho',{}))}, hne={len(ui_data.get('hne',{}))}")

    print("Generating state names for raj/bho/hne...")
    states_data = call_gemini(build_states_prompt())
    print(f"  Got states: raj={len(states_data.get('raj',{}))}, bho={len(states_data.get('bho',{}))}, hne={len(states_data.get('hne',{}))}")

    # ── Write i18n files ───────────────────────────────────────────────────
    for code in ["raj", "bho", "hne"]:
        lang_ui = ui_data.get(code, {})
        if lang_ui:
            out_path = I18N_DIR / f"{code}.json"
            out_path.write_text(json.dumps(lang_ui, ensure_ascii=False, indent=2))
            print(f"  Written {out_path.name}  ({len(lang_ui)} keys)")
        else:
            print(f"  WARN: no UI data for {code}")

    # ── Merge into states.json ─────────────────────────────────────────────
    states_full = json.loads((I18N_DIR / "states.json").read_text())
    for code in ["raj", "bho", "hne"]:
        lang_states = states_data.get(code, {})
        if lang_states:
            states_full[code] = lang_states
            print(f"  Added {len(lang_states)} state entries for {code}")
        else:
            print(f"  WARN: no state data for {code}")

    (I18N_DIR / "states.json").write_text(json.dumps(states_full, ensure_ascii=False, indent=2))
    print("  Updated states.json")

    print("\nDone!")


if __name__ == "__main__":
    main()
