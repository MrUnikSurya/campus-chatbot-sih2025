import json
import difflib
import uuid
import threading
import re
from pathlib import Path

from flask import Flask, request, jsonify, session, render_template
from googletrans import Translator

# ---------------------------
# Config
# ---------------------------
APP_SECRET_KEY = "123456"  # set via env var in production
FAQ_PATH = Path("faq.json")
INTENT_MATCH_THRESHOLD = 0.6  # fuzzy match threshold

# ---------------------------
# App setup
# ---------------------------
app = Flask(__name__, static_folder="static", template_folder="../frontend")
app.secret_key = APP_SECRET_KEY

translator = Translator()

# in-memory server-side storage (ephemeral)
server_memory = {}  # session_id -> dict
memory_lock = threading.Lock()

# ---------------------------
# Load FAQ / rule-based intents
# ---------------------------
def load_faq(path=FAQ_PATH):
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

faq = load_faq()

# Normalize text: lowercase, remove extra whitespace
def normalize_text(s: str) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    # Keep Unicode word characters (do not strip non-latin completely), but remove excessive punctuation
    # We remove just common punctuation for fuzzy matching.
    s = re.sub(r"[^\w\s\u0900-\u097F\u0980-\u09FF\u0A00-\u0A7F\u0A80-\u0AFF]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s

# ---------------------------
# Intent matching: exact -> substring -> fuzzy
# ---------------------------
def find_intent(user_text: str):
    txt = normalize_text(user_text)
    best_entry = None
    best_score = 0.0

    for entry in faq:
        patterns = entry.get("patterns", [])
        for p in patterns:
            p_norm = normalize_text(p)
            # exact match
            if p_norm == txt:
                return entry, 1.0
            # substring
            if p_norm and (p_norm in txt or txt in p_norm):
                return entry, 0.95
            # fuzzy (sequence matcher)
            score = difflib.SequenceMatcher(None, txt, p_norm).ratio()
            if score > best_score:
                best_score = score
                best_entry = entry

    if best_score >= INTENT_MATCH_THRESHOLD:
        return best_entry, best_score
    return None, best_score

# ---------------------------
# Generate a simple reply (English)
# ---------------------------
def generate_response(english_text: str, session_id: str) -> str:
    lower = english_text.lower().strip()

    # Check if user asks for last question stored in session
    if any(k in lower for k in ("repeat", "again", "what was my last", "last question")):
        mem = server_memory.get(session_id, {})
        last_q = mem.get("last_question")
        if last_q:
            return f'Your last question I have is: "{last_q}". Do you want me to answer it now?'
        else:
            return "I don't have any previous question stored for this session."

    # try rule-based intents
    intent_entry, score = find_intent(english_text)
    if intent_entry:
        return intent_entry.get("response", "Okay.")

    # fallback
    return "Sorry, I didn't understand that. Could you rephrase or ask something else?"

# ---------------------------
# Root route -> render frontend
# ---------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    # ensure a session_id exists (so Flask sets session cookie on first page load)
    if request.method == ["GET"]:
        return render_template("index.html")
    elif request.method == ["POST"]:
        if "session_id" not in session:
            session["session_id"] = str(uuid.uuid4())
    return render_template("index.html")

# ---------------------------
# Chat endpoint
# ---------------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True, silent=True)
    if not data or "query" not in data:
        return jsonify({"error": "Please send JSON with a 'query' field."}), 400

    user_text = str(data.get("query") or "").strip()
    if user_text == "":
        return jsonify({"error": "Empty 'query' provided."}), 400

    # determine session id (client may provide one, otherwise use Flask session)
    client_sid = data.get("session_id")
    if not client_sid:
        if "session_id" not in session:
            session["session_id"] = str(uuid.uuid4())
        client_sid = session["session_id"]

    # detect language robustly
    detected_lang = "en"
    try:
        detect_res = translator.detect(user_text)
        if isinstance(detect_res, (list, tuple)) and len(detect_res) > 0:
            detected_lang = getattr(detect_res[0], "lang", str(detect_res[0]) if detect_res[0] else "en")
        else:
            detected_lang = getattr(detect_res, "lang", "en")
        if not detected_lang:
            detected_lang = "en"
    except Exception:
        detected_lang = "en"

    # optional override from client
    forced_lang = data.get("force_lang")
    if forced_lang:
        detected_lang = forced_lang

    # translate to English if needed
    translated_to_en = user_text
    if detected_lang != "en":
        try:
            t = translator.translate(user_text, src=detected_lang, dest="en")
            translated_to_en = getattr(t, "text", user_text)
        except Exception:
            translated_to_en = user_text

    # save last question in both Flask session and server_memory (thread-safe)
    session["last_question"] = user_text
    with memory_lock:
        if client_sid not in server_memory:
            server_memory[client_sid] = {}
        server_memory[client_sid]["last_question"] = user_text

    # generate reply (in English)
    reply_en = generate_response(translated_to_en, client_sid)

    # translate reply back to user's language if required
    translated_reply = reply_en
    if detected_lang != "en":
        try:
            t2 = translator.translate(reply_en, src="en", dest=detected_lang)
            translated_reply = getattr(t2, "text", reply_en)
        except Exception:
            translated_reply = reply_en

    out = {
        "reply": translated_reply,
        "reply_in_english": reply_en,
        "detected_language": detected_lang,
        "translated_to_english": translated_to_en,
        "session_id": client_sid,
        "server_memory": {"last_question": server_memory.get(client_sid, {}).get("last_question")}
    }
    return jsonify(out), 200

# ---------------------------
# Health check
# ---------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# ---------------------------
# Run (dev)
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
