import hashlib
import json
import logging
import os
import re
import sys
from collections import defaultdict, deque
from contextlib import suppress
from datetime import datetime
from io import BytesIO
from pathlib import Path
from threading import Lock
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

for env_path in (
    os.path.join(CURRENT_DIR, ".env"),
    os.path.join(ROOT_DIR, ".env"),
):
    load_dotenv(dotenv_path=env_path)

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from logging.handlers import RotatingFileHandler

from database import (
    clear_session as clear_session_rows,
    create_auth_token,
    create_user,
    get_history,
    get_user_by_email,
    get_user_by_token,
    hash_password,
    init_db,
    save_message,
    stats,
    get_user_profile,
    create_or_update_user_profile,
    save_profile_picture,
    get_profile_pictures_dir,
)
import requai_deploy.app as model_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

LOG_DIR = os.path.join(CURRENT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "backend.log"), maxBytes=1_000_000, backupCount=3
)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
)
logging.getLogger().addHandler(file_handler)

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = int(
    os.environ.get("MAX_CONTENT_LENGTH", str(8 * 1024 * 1024))
)
init_db()


# ============================================================
# HELPERS — rate limiting, file upload wrapper
# ============================================================

class _MemoryUpload:
    """Wraps raw bytes so requai_deploy's PDF parser can consume them."""
    def __init__(self, data: bytes, filename: str):
        self._data = data
        self.filename = filename

    def save(self, destination: str):
        with open(destination, "wb") as fh:
            fh.write(self._data)


class _TokenBucket:
    """Sliding-window rate limiter (capacity requests per 60 seconds)."""
    def __init__(self, capacity: int = 20):
        self.capacity = capacity
        self._buckets: dict = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str):
        now = datetime.utcnow().timestamp()
        with self._lock:
            bucket = self._buckets[key]
            while bucket and bucket[0] < now - 60:
                bucket.popleft()
            if len(bucket) >= self.capacity:
                return False, round(60 - (now - bucket[0]), 2)
            bucket.append(now)
            return True, 0.0


request_limiter = _TokenBucket(
    capacity=int(os.environ.get("CHAT_RATE_LIMIT", "20"))
)


def rate_limited():
    ip = request.headers.get(
        "X-Forwarded-For", request.remote_addr or "unknown"
    ).split(",")[0].strip()
    allowed, retry_after = request_limiter.allow(f"{ip}:{request.endpoint}")
    if not allowed:
        resp = jsonify({
            "error": "Rate limit exceeded",
            "retry_after": retry_after,
            "code": 429,
        })
        resp.status_code = 429
        resp.headers["Retry-After"] = str(retry_after)
        return resp
    return None


@app.errorhandler(HTTPException)
def handle_http_exception(exc):
    return jsonify({"error": exc.description, "code": exc.code}), exc.code


@app.errorhandler(Exception)
def handle_unexpected_exception(exc):
    logging.exception("Unhandled error: %s", exc)
    return jsonify({"error": "Internal server error"}), 500


# ============================================================
# EMPLOYMENT SCOPE
# ============================================================

_EMPLOYMENT_EXACT = {
    "job", "jobs", "cv", "resume", "anem", "hire", "hired", "hiring",
    "salary", "salaries", "vacancy", "vacancies", "internship",
    "freelance", "recruitment", "recruiter", "employment", "unemployed",
    "emploi", "recrutement", "poste", "salaire", "candidature",
    "offre", "stage", "télétravail",
}

_EMPLOYMENT_SUBSTRING = {
    "job search", "job offer", "job opening", "work experience",
    "cover letter", "job application", "career advice", "interview tips",
    "work permit", "labor law", "labour law", "minimum wage", "job market",
    "offre d'emploi", "recherche d'emploi", "contrat de travail",
    "droit du travail", "marché du travail",
    "وظيفة", "وظائف", "خدمة", "شغل", "توظيف", "راتب",
    "سيرة ذاتية", "مقابلة عمل", "فرصة عمل", "منصب",
    "أنام", "تدريب مهني", "مهارة", "عروض العمل",
}

_GREETING_WORDS = {
    "hi", "hello", "hey", "good morning", "good afternoon",
    "good evening", "howdy", "greetings", "bonjour", "salut",
    "bonsoir", "مرحبا", "السلام عليكم", "أهلا",
    "صباح الخير", "مساء الخير",
}


def is_employment_related(text: str) -> bool:
    if not isinstance(text, str) or not text.strip():
        return False
    if text.lower().strip() in _GREETING_WORDS:
        return False
    lowered = text.lower()
    for kw in _EMPLOYMENT_EXACT:
        if kw.isascii():
            if re.search(rf"\b{re.escape(kw)}\b", lowered):
                return True
        else:
            if kw in text:
                return True
    for kw in _EMPLOYMENT_SUBSTRING:
        if kw.isascii():
            if kw in lowered:
                return True
        else:
            if kw in text:
                return True
    return False


# ============================================================
# LANGUAGE DETECTION
# ============================================================

_FRENCH_HINTS = {
    "je ", "tu ", "il ", "elle ", "nous ", "vous ", "ils ",
    "emploi", "travail", "recrutement", "poste", "salaire",
    "bonjour", "merci", "cherche", "veux", "besoin",
    "offre", "stage", "expérience", "compétence",
}

_LATIN_DARIJA_HINTS = {
    "khdma", "khedma", "khadma", "nekhdem", "nheb",
    "baghi", "bghit", "wela", "blad", "chghol",
}


def detect_language(text: str, requested: str = "en") -> str:
    if not text or not text.strip():
        return requested or "en"
    if re.search(r"[\u0600-\u06FF]", text):
        return "ar"
    lowered = text.lower()
    if any(hint in lowered for hint in _FRENCH_HINTS):
        return "fr"
    if any(hint in lowered.split() for hint in _LATIN_DARIJA_HINTS):
        return "ar"
    return requested or "en"


# ============================================================
# CONTEXT EXTRACTION
#
# These three functions are the core of multi-turn awareness.
# They scan conversation history, build a running preferences
# dict, and decide whether to ask a follow-up question.
# ============================================================

# Job title signals — used in preference extraction
_JOB_TITLE_PATTERNS = [
    # Software
    r"\b(software engineer|software developer|web developer|"
    r"frontend developer|backend developer|fullstack developer|"
    r"full[- ]?stack developer|mobile developer|"
    r"devops engineer|cloud engineer|data scientist|"
    r"data analyst|data engineer|machine learning engineer|"
    r"ml engineer|ai engineer|cybersecurity engineer|"
    r"network engineer|system administrator|it support|"
    r"database administrator|ui[/ ]ux designer|programmer|developer)\b",
    # Business
    r"\b(project manager|product manager|business analyst|"
    r"operations manager|supply chain manager|logistics coordinator|"
    r"marketing manager|marketing specialist|sales manager|"
    r"sales representative|hr manager|hr specialist|"
    r"finance manager|financial analyst|accountant|auditor|"
    r"tax consultant|bank teller|bank officer|controller)\b",
    # Engineering
    r"\b(civil engineer|mechanical engineer|electrical engineer|"
    r"chemical engineer|petroleum engineer|industrial engineer|"
    r"architect|engineer|technician)\b",
    # Healthcare
    r"\b(doctor|general practitioner|pharmacist|nurse|dentist|"
    r"medical officer)\b",
    # Education
    r"\b(teacher|professor|university professor|trainer|instructor)\b",
    # Legal
    r"\b(lawyer|legal advisor|notary)\b",
    # Trades
    r"\b(electrician|plumber|welder|mechanic|driver|"
    r"security guard|receptionist|administrative assistant|"
    r"customer service|coordinator|specialist|supervisor|"
    r"executive|officer|assistant|consultant|manager|director)\b",
    # Arabic / Darija job titles
    r"(مهندس|مطور|محاسب|طبيب|ممرض|أستاذ|"
    r"سائق|مدير|محلل|مصمم|مبرمج|محامي|تقني)",
]

_JOB_TITLE_RE = re.compile(
    "|".join(_JOB_TITLE_PATTERNS),
    re.IGNORECASE,
)

# Refinement signals — user is changing a previous search
_REFINEMENT_PATTERNS = [
    r"\bwhat about\b", r"\bhow about\b", r"\band in\b",
    r"\binstead\b", r"\bchange\b", r"\bswitch\b",
    r"\bdifferent\b", r"\bother\b", r"\banother\b",
    r"\bwhat about in\b", r"\bshow me in\b",
    r"\bmais (pour|à|en)\b",
    r"وماذا عن", r"ماذا عن", r"وفي", r"وبدلاً",
]

_REFINEMENT_RE = re.compile(
    "|".join(_REFINEMENT_PATTERNS),
    re.IGNORECASE,
)


def extract_job_preferences_from_history(history: list) -> dict:
    """
    Scan the full conversation history (user + assistant turns) and
    extract cumulative job preferences.

    Returns a dict with keys:
        job_title   : str | None   — most recently mentioned job title
        location    : list | None  — list of wilayas
        work_type   : str | None   — e.g. "remote", "full_time"
        skills      : list         — accumulated skill mentions
        last_jobs   : list         — jobs returned in the last search turn
        turn_count  : int          — number of user turns so far
    """
    prefs = {
        "job_title":  None,
        "location":   None,
        "work_type":  None,
        "skills":     [],
        "last_jobs":  [],
        "turn_count": 0,
    }

    if not history:
        return prefs

    for turn in history:
        role    = turn.get("role", "")
        content = turn.get("content", "")
        meta    = turn.get("metadata") or {}

        # ── User turns: extract job title, location, skills ──────────
        if role == "user":
            prefs["turn_count"] += 1

            # Job title extraction
            m = _JOB_TITLE_RE.search(content)
            if m:
                prefs["job_title"] = m.group(0).strip().lower()

            # Location / wilaya extraction (uses model's entity extractor)
            try:
                entities = model_app.extract_entities_api(content)
                if entities.get("location"):
                    prefs["location"] = entities["location"]
                if entities.get("work_type"):
                    prefs["work_type"] = entities["work_type"]
                if entities.get("skills"):
                    for skill in entities["skills"]:
                        if skill not in prefs["skills"]:
                            prefs["skills"].append(skill)
            except Exception as exc:
                logger.debug("Entity extraction in history failed: %s", exc)

        # ── Assistant turns: capture jobs from last search ────────────
        if role == "assistant":
            if isinstance(meta, dict) and meta.get("jobs"):
                prefs["last_jobs"] = meta["jobs"]
            # Also check if jobs were embedded directly in the content dict
            if isinstance(content, dict) and content.get("jobs"):
                prefs["last_jobs"] = content["jobs"]

    return prefs


def needs_clarification(
    message: str,
    intent: str,
    entities: dict,
    prefs: dict,
) -> tuple:
    """
    Decide whether to ask the user a clarifying question instead of
    running a job search immediately.

    Returns (should_ask: bool, question_key: str)
    where question_key is one of:
        "ask_job_type"  — we don't know what kind of job they want
        "ask_location"  — job type known but no location provided yet
        ""              — no clarification needed
    """
    # If we already have a job title from history, no need to ask again
    has_job_title = bool(
        prefs.get("job_title")
        or entities.get("skills")
        or _JOB_TITLE_RE.search(message)
    )

    # If the user is refining a previous search ("what about in Algiers?"),
    # they already provided context — don't ask again
    is_refinement = bool(_REFINEMENT_RE.search(message))
    if is_refinement and prefs.get("job_title"):
        return False, ""

    # If we have a CV text, skills are implied — skip clarification
    if entities.get("skills"):
        has_job_title = True

    # For job_search and cv_upload intents only
    if intent not in {"job_search", "cv_upload"}:
        return False, ""

    if not has_job_title:
        return True, "ask_job_type"

    return False, ""


# Clarification question templates
_CLARIFICATION_QUESTIONS = {
    "ask_job_type": {
        "en": (
            "I'd love to help you find a job! "
            "**What type of job are you looking for?**\n\n"
            "For example:\n"
            "• Software engineer, data scientist, developer\n"
            "• Accountant, financial analyst\n"
            "• Doctor, nurse, pharmacist\n"
            "• Teacher, trainer\n"
            "• Manager, sales, marketing\n\n"
            "_You can also mention a city or wilaya if you have a preference._"
        ),
        "fr": (
            "Je serais ravi de vous aider à trouver un emploi ! "
            "**Quel type de poste recherchez-vous ?**\n\n"
            "Par exemple :\n"
            "• Ingénieur logiciel, data scientist, développeur\n"
            "• Comptable, analyste financier\n"
            "• Médecin, infirmier, pharmacien\n"
            "• Enseignant, formateur\n"
            "• Manager, commercial, marketing\n\n"
            "_Vous pouvez aussi mentionner une ville ou wilaya._"
        ),
        "ar": (
            "يسعدني مساعدتك في البحث عن عمل! "
            "**ما نوع الوظيفة التي تبحث عنها؟**\n\n"
            "على سبيل المثال:\n"
            "• مهندس برمجيات، عالم بيانات، مطور\n"
            "• محاسب، محلل مالي\n"
            "• طبيب، ممرض، صيدلاني\n"
            "• أستاذ، مدرب\n"
            "• مدير، مبيعات، تسويق\n\n"
            "_يمكنك أيضاً ذكر مدينة أو ولاية إن أردت._"
        ),
    },
    "ask_location": {
        "en": (
            "Got it — I'm looking for **{job_title}** jobs. "
            "Do you have a preferred city or wilaya in Algeria?\n\n"
            "_Or I can search across all of Algeria if you prefer._"
        ),
        "fr": (
            "Compris — je cherche des postes de **{job_title}**. "
            "Avez-vous une ville ou wilaya préférée en Algérie ?\n\n"
            "_Ou je peux rechercher dans toute l'Algérie si vous préférez._"
        ),
        "ar": (
            "فهمت — سأبحث عن وظائف **{job_title}**. "
            "هل تفضل مدينة أو ولاية معينة في الجزائر؟\n\n"
            "_أو يمكنني البحث في كامل الجزائر إذا أردت._"
        ),
    },
}


def get_clarification_response(question_key: str, lang: str, prefs: dict) -> str:
    template = _CLARIFICATION_QUESTIONS.get(question_key, {})
    text = template.get(lang, template.get("en", ""))
    return text.format(job_title=prefs.get("job_title", ""))


# ============================================================
# CONTEXT-AWARE PROMPT BUILDER
# ============================================================

def build_context_aware_prompt(
    message: str,
    intent: str,
    jobs: list,
    prefs: dict,
    entities: dict,
    language: str,
) -> str:
    """
    Build a rich LLM prompt that includes:
      - The current user message
      - Extracted preferences from conversation history
      - Jobs found in this search turn
      - Jobs found in previous search turns (for follow-up references)
      - Specific instructions to stay in English and be concise

    The prompt structure guides the LLM to:
      - Reference previous context naturally
      - Present new results clearly
      - Handle refinements ("what about Algiers?") gracefully
      - Never switch language
    """
    # Build context block from preferences
    ctx_parts = []
    if prefs.get("job_title"):
        ctx_parts.append(f"Job type sought: {prefs['job_title']}")
    if prefs.get("location"):
        ctx_parts.append(f"Location: {', '.join(prefs['location'])}")
    if prefs.get("work_type"):
        ctx_parts.append(f"Work type: {prefs['work_type']}")
    if prefs.get("skills"):
        ctx_parts.append(f"Skills: {', '.join(prefs['skills'][:6])}")
    context_block = "\n".join(ctx_parts) if ctx_parts else "No prior preferences"

    # Build previous jobs block (for follow-up turns)
    prev_jobs_block = ""
    if prefs.get("last_jobs") and not jobs:
        # User is asking a follow-up about previously found jobs
        prev_list = "\n".join(
            f"  {i+1}. {j.get('Job Title','?')} at {j.get('Company','?')} "
            f"({j.get('location','?')}) — {j.get('match_score',0):.0%} match"
            for i, j in enumerate(prefs["last_jobs"][:5])
        )
        prev_jobs_block = f"\nPreviously found jobs:\n{prev_list}\n"

    # Build current jobs block
    if jobs:
        jobs_list = "\n".join(
            f"  {i+1}. {j.get('Job Title','?')} at {j.get('Company','?')} "
            f"({j.get('location','?')}) — "
            f"{j.get('match_score',0):.0%} match"
            + (
                f" — {j['algerian_salary_range']}"
                if j.get("algerian_salary_range") and
                   str(j["algerian_salary_range"]) not in {"nan","None",""}
                else (
                    f" — {j['salary_dzd']:,.0f} DZD"
                    if j.get("salary_dzd") and j["salary_dzd"] == j["salary_dzd"]
                    else ""
                )
            )
            for i, j in enumerate(jobs)
        )
        jobs_block = f"\nJobs found ({len(jobs)} results):\n{jobs_list}\n"
    else:
        jobs_block = "\nNo matching jobs found for this search.\n"

    # Detect if this is a refinement turn
    is_refinement = bool(_REFINEMENT_RE.search(message))
    refinement_note = (
        "\nNote: The user is refining their previous search. "
        "Acknowledge the change naturally (e.g. 'Here are developer jobs in Algiers...')"
        if is_refinement else ""
    )

    # Detect if this is a follow-up about previously shown jobs
    is_followup_about_previous = (
        bool(prev_jobs_block)
        and intent not in {"job_search", "cv_upload"}
    )
    followup_note = (
        "\nNote: The user is asking about previously shown jobs. "
        "Reference them naturally."
        if is_followup_about_previous else ""
    )

    prompt = f"""You are RequAI, an employment assistant for Algeria.

CONVERSATION CONTEXT:
{context_block}
{prev_jobs_block}{jobs_block}{refinement_note}{followup_note}

USER MESSAGE: "{message}"

INSTRUCTIONS:
- Always respond in English only, regardless of the user's language.
- Present job results clearly with title, company, location, and match score.
- If no jobs were found, give 3 practical tips (ANEM registration, nearby wilayas, related titles).
- Reference previous conversation context naturally when relevant.
- Be concise and professional. Maximum 200 words.
- Do not repeat the same information twice.
- Do not start with filler phrases like "Of course!" or "Great question!".
"""
    return prompt


# ============================================================
# QUERY TRANSLATION (for TF-IDF matching only)
# ============================================================

def translate_for_matching(text: str, lang: str, entities: dict) -> str:
    if lang == "en":
        return text
    try:
        expanded = model_app.expand_search_text(text, entities or {})
        if expanded and expanded.strip() and expanded.strip() != text.strip():
            return expanded
    except Exception as exc:
        logger.debug("expand_search_text failed: %s", exc)
    try:
        from requai_deploy.app import (
            QUERY_TRANSLATIONS,
            ARABIC_WILAYA_ALIASES,
            LATIN_WILAYA_ALIASES,
        )
        terms = []
        for src, dst in QUERY_TRANSLATIONS.items():
            if src in text or src.lower() in text.lower():
                terms.append(dst)
        for alias, wilaya in ARABIC_WILAYA_ALIASES.items():
            if alias in text:
                terms.append(wilaya)
        for alias, wilaya in LATIN_WILAYA_ALIASES.items():
            if alias.lower() in text.lower():
                terms.append(wilaya)
        if terms:
            return " ".join(dict.fromkeys(terms))
    except Exception as exc:
        logger.debug("Direct translation failed: %s", exc)
    if getattr(model_app, "groq_client", None):
        try:
            translated = model_app.ask_llm(
                [{"role": "user",
                  "content": f"Translate to English (output only): {text}"}],
                100,
            )
            if translated and not translated.startswith("LLM error"):
                return translated
        except Exception as exc:
            logger.debug("LLM translation failed: %s", exc)
    return text


# ============================================================
# STATIC RESPONSE TEMPLATES
# ============================================================

GREETING_RESPONSES = {
    "en": (
        "Hello! I'm **RequAI**, your employment assistant for Algeria. 👋\n\n"
        "I can help you with:\n"
        "• Finding jobs in Algeria\n"
        "• Writing or improving your CV\n"
        "• ANEM registration and procedures\n"
        "• Salary information\n"
        "• Interview preparation\n\n"
        "What are you looking for today?"
    ),
    "fr": (
        "Bonjour ! Je suis **RequAI**, votre assistant emploi pour l'Algérie. 👋\n\n"
        "Je peux vous aider à :\n"
        "• Trouver des emplois en Algérie\n"
        "• Rédiger ou améliorer votre CV\n"
        "• Vous inscrire à l'ANEM\n"
        "• Obtenir des informations sur les salaires\n"
        "• Préparer vos entretiens\n\n"
        "Que recherchez-vous aujourd'hui ?"
    ),
    "ar": (
        "مرحباً! أنا **RequAI**، مساعدك للتوظيف في الجزائر. 👋\n\n"
        "أستطيع مساعدتك في:\n"
        "• البحث عن وظائف في الجزائر\n"
        "• كتابة أو تحسين سيرتك الذاتية\n"
        "• التسجيل في الوكالة الوطنية للتشغيل\n"
        "• معلومات الرواتب\n"
        "• التحضير للمقابلات\n\n"
        "بماذا يمكنني مساعدتك اليوم؟"
    ),
}

OUT_OF_SCOPE_RESPONSES = {
    "en": (
        "I'm RequAI, an employment assistant specialized in the "
        "Algerian job market. I can only help with:\n\n"
        "• Job search and vacancies in Algeria\n"
        "• CV writing and improvement\n"
        "• ANEM registration and procedures\n"
        "• Salary information and labor law\n"
        "• Interview preparation\n\n"
        "Please ask me something related to employment in Algeria."
    ),
    "fr": (
        "Je suis RequAI, un assistant emploi spécialisé dans le marché "
        "du travail algérien. Je peux uniquement vous aider avec :\n\n"
        "• Recherche d'emplois en Algérie\n"
        "• Rédaction et amélioration de CV\n"
        "• Inscription et procédures ANEM\n"
        "• Informations sur les salaires et le droit du travail\n"
        "• Préparation aux entretiens\n\n"
        "Posez-moi une question liée à l'emploi en Algérie."
    ),
    "ar": (
        "أنا RequAI، مساعد توظيف متخصص في سوق العمل الجزائري. "
        "أستطيع فقط مساعدتك في:\n\n"
        "• البحث عن وظائف في الجزائر\n"
        "• كتابة وتحسين السيرة الذاتية\n"
        "• التسجيل في الوكالة الوطنية للتشغيل\n"
        "• معلومات الرواتب وقانون العمل\n"
        "• التحضير للمقابلات\n\n"
        "يرجى طرح سؤال متعلق بالتوظيف في الجزائر."
    ),
}


# ============================================================
# SESSION / AUTH HELPERS
# ============================================================

def current_user_from_request():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.removeprefix("Bearer ").strip()
    return get_user_by_token(token) if token else None


def get_session_history(session_id: str) -> list:
    return get_history(session_id, limit=40)


def build_llm_messages(history: list, user_msg: str) -> list:
    messages = [{"role": "system", "content": model_app.SYSTEM_PROMPT}]
    messages.extend(
        {"role": item["role"], "content": item["content"]}
        for item in history[-20:]
    )
    messages.append({"role": "user", "content": user_msg})
    return messages


def _save_turn(
    session_id: str,
    user_msg: str,
    assistant_msg: str,
    intent: str,
    conf: float,
    entities: dict,
    behavior: dict,
    security: dict,
    jobs: list,
):
    with suppress(Exception):
        save_message(session_id, "user", user_msg, {"message": user_msg})
        save_message(
            session_id, "assistant", assistant_msg,
            {
                "response":   assistant_msg,
                "jobs":       jobs,
                "intent":     intent,
                "confidence": round(conf, 4),
                "entities":   entities,
                "behavior":   behavior,
                "security":   security,
            },
        )


# ============================================================
# ROUTES — meta
# ============================================================

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "name":    "RequAI Backend",
        "version": "3.2",
        "routes": [
            "POST /chat",
            "POST /upload_cv",
            "GET  /session/<id>",
            "DELETE /session/<id>",
            "GET  /health",
            "POST /auth/register",
            "POST /auth/login",
            "GET  /auth/me",
            "GET  /auth/profile",
            "PUT  /auth/profile",
            "POST /auth/profile/picture",
        ],
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "db":     stats(),
        "llm":    "connected" if getattr(model_app, "groq_client", None)
                  else "not configured",
        "jobs":   len(model_app.df_jobs)
                  if getattr(model_app, "df_jobs", None) is not None else 0,
        "chunks": len(model_app.df_chunks)
                  if getattr(model_app, "df_chunks", None) is not None else 0,
    })


# ============================================================
# AUTH ROUTES
# ============================================================

@app.route("/auth/register", methods=["POST"])
def auth_register():
    data      = request.get_json(silent=True) or {}
    full_name = (data.get("fullName") or data.get("full_name") or "").strip()
    email     = (data.get("email") or "").strip().lower()
    password  = data.get("password") or ""
    if not full_name or not email or not password:
        return jsonify({"detail": "fullName, email, and password are required"}), 400
    if len(password) < 6:
        return jsonify({"detail": "Password must be at least 6 characters"}), 400
    if get_user_by_email(email):
        return jsonify({"detail": "Email already registered"}), 409
    user_id = create_user(full_name, email, password)
    create_or_update_user_profile(user_id)
    token = create_auth_token(user_id)
    user  = get_user_by_email(email)
    return jsonify({
        "id":           user_id,
        "fullName":     user["full_name"],
        "email":        user["email"],
        "access_token": token,
        "token_type":   "bearer",
    }), 201


@app.route("/auth/login", methods=["POST"])
def auth_login():
    data     = request.get_json(silent=True) or {}
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user     = get_user_by_email(email)
    if not user or user["password_hash"] != hash_password(password):
        return jsonify({"detail": "Invalid email or password"}), 401
    token = create_auth_token(user["id"])
    return jsonify({"access_token": token, "token_type": "bearer"})


@app.route("/auth/me", methods=["GET"])
def auth_me():
    user = current_user_from_request()
    if not user:
        return jsonify({"detail": "Not authenticated"}), 401
    return jsonify({
        "id":       user["id"],
        "fullName": user["full_name"],
        "email":    user["email"],
    })


def _profile_response(profile: dict) -> dict:
    pic_url = None
    if profile.get("profile_picture_path"):
        pic_url = (
            f"/profile-pictures/"
            f"{profile['profile_picture_path'].split('/')[-1]}"
        )
    return {
        "userId":           profile["user_id"],
        "avatarId":         profile["avatar_id"],
        "bio":              profile["bio"],
        "location":         profile["location"],
        "profession":       profile["profession"],
        "website":          profile["website"],
        "preferences":      profile["preferences"],
        "profilePictureUrl": pic_url,
        "updatedAt":        profile["updated_at"],
    }


@app.route("/auth/profile", methods=["GET"])
def get_profile():
    user = current_user_from_request()
    if not user:
        return jsonify({"detail": "Not authenticated"}), 401
    profile = get_user_profile(user["id"]) or {}
    if not profile:
        create_or_update_user_profile(user["id"])
        profile = get_user_profile(user["id"])
    return jsonify(_profile_response(profile))


@app.route("/auth/profile", methods=["PUT"])
def update_profile():
    user = current_user_from_request()
    if not user:
        return jsonify({"detail": "Not authenticated"}), 401
    data = request.get_json(silent=True) or {}
    create_or_update_user_profile(
        user_id    = user["id"],
        avatar_id  = data.get("avatarId"),
        bio        = data.get("bio"),
        location   = data.get("location"),
        profession = data.get("profession"),
        website    = data.get("website"),
        preferences= data.get("preferences"),
    )
    return jsonify(_profile_response(get_user_profile(user["id"])))


@app.route("/auth/profile/picture", methods=["POST"])
def upload_profile_picture():
    user = current_user_from_request()
    if not user:
        return jsonify({"detail": "Not authenticated"}), 401
    if "file" not in request.files:
        return jsonify({"detail": "No file part in request"}), 400
    file = request.files["file"]
    if not file.filename:
        return jsonify({"detail": "No file selected"}), 400
    ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else ""
    if ext not in {"png", "jpg", "jpeg", "gif", "webp"}:
        return jsonify({"detail": "File type not allowed"}), 400
    data = file.read()
    if len(data) > 5 * 1024 * 1024:
        return jsonify({"detail": "File too large. Maximum 5 MB"}), 400
    path = save_profile_picture(user["id"], data, file.filename)
    if not path:
        return jsonify({"detail": "Error saving picture"}), 500
    pic_url = f"/profile-pictures/{path.split('/')[-1]}" if path else None
    return jsonify({
        "message":          "Profile picture uploaded successfully",
        "profilePictureUrl": pic_url,
    }), 200


@app.route("/profile-pictures/<filename>", methods=["GET"])
def serve_profile_picture(filename):
    if ".." in filename or "/" in filename:
        return jsonify({"detail": "Invalid filename"}), 400
    pic_dir  = get_profile_pictures_dir()
    filepath = os.path.join(pic_dir, filename)
    if not os.path.abspath(filepath).startswith(os.path.abspath(pic_dir)):
        return jsonify({"detail": "File not found"}), 404
    if not os.path.exists(filepath):
        return jsonify({"detail": "File not found"}), 404
    from flask import send_file
    return send_file(filepath, mimetype="image/jpeg")


# ============================================================
# MAIN CHAT ROUTE — multi-turn context aware
# ============================================================

@app.route("/chat", methods=["POST"])
def chat():
    # ── Rate limit ────────────────────────────────────────
    limited = rate_limited()
    if limited:
        return limited

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # ── Extract fields ────────────────────────────────────
    ip            = request.headers.get(
        "X-Forwarded-For", request.remote_addr or "unknown"
    ).split(",")[0].strip()
    session_id    = data.get("session_id", "default")
    user_id       = hashlib.md5(f"{ip}:{session_id}".encode()).hexdigest()[:12]
    raw_message   = (data.get("message") or "").strip()
    cv_text       = data.get("cv_text", None)
    masked        = data.get("masked", False)
    req_lang      = data.get("language", "en")
    frontend_hist = data.get("history", [])

    if not raw_message:
        return jsonify({"error": "message is required"}), 400

    # ── Security validation ───────────────────────────────
    msg_val    = model_app._sec_validator.validate(raw_message, "message")
    message    = msg_val["sanitized"]
    cv_threats = []
    if cv_text:
        cv_val     = model_app._sec_validator.validate(cv_text, "cv_text")
        cv_text    = cv_val["sanitized"]
        cv_threats = cv_val["threats"]
    security = {"message_threats": msg_val["threats"], "cv_threats": cv_threats}

    # ── Behavioral classification ─────────────────────────
    behavior = model_app._behavior_clf.classify(message, user_id=user_id)

    # ── Language detection ────────────────────────────────
    language = detect_language(message, req_lang)

    # ── Load session history ──────────────────────────────
    # Prefer history sent from frontend (includes metadata for context
    # extraction). Fall back to database.
    history = frontend_hist if frontend_hist else get_session_history(session_id)

    # ── Extract preferences from full conversation history ─
    # This is what makes the chatbot context-aware across turns.
    prefs = extract_job_preferences_from_history(history)
    logger.info(
        "Extracted prefs | session=%s job_title=%s location=%s turn=%d",
        session_id,
        prefs.get("job_title"),
        prefs.get("location"),
        prefs.get("turn_count"),
    )

    # ── Intent + entity detection ─────────────────────────
    intent = "general_query"
    conf   = 0.0
    if getattr(model_app, "intent_pipeline", None) is not None:
        try:
            intent = model_app.intent_pipeline.predict([message])[0]
            conf   = float(
                model_app.intent_pipeline.predict_proba([message]).max()
            )
        except Exception:
            logger.exception("Intent classification failed")
    entities = model_app.extract_entities_api(message)

    # Merge entities with history preferences so that location/skills
    # from earlier turns are available even when not repeated
    if not entities.get("location") and prefs.get("location"):
        entities["location"] = prefs["location"]
    if not entities.get("skills") and prefs.get("skills"):
        entities["skills"] = prefs["skills"]

    # ─────────────────────────────────────────────────────
    # 1. GREETING
    # ─────────────────────────────────────────────────────
    is_greeting = (
        intent == "greeting"
        or message.lower().strip() in _GREETING_WORDS
    )
    if is_greeting:
        response_text = GREETING_RESPONSES.get(language, GREETING_RESPONSES["en"])
        _save_turn(session_id, message, response_text,
                   intent="greeting", conf=1.0, entities={},
                   behavior=behavior, security=security, jobs=[])
        return jsonify({
            "session_id": session_id,
            "intent":     "greeting",
            "confidence": 1.0,
            "entities":   {},
            "response":   response_text,
            "jobs":       [],
            "behavior":   behavior,
            "security":   security,
        })

    # ─────────────────────────────────────────────────────
    # 2. SCOPE CHECK
    # ─────────────────────────────────────────────────────
    # If the user is in an active job-search conversation (turn_count > 1
    # and we already have preferences), treat follow-up messages as
    # employment-related even if they don't contain keywords.
    in_active_session = (
        prefs.get("turn_count", 0) > 0
        and (prefs.get("job_title") or prefs.get("last_jobs"))
    )
    if not in_active_session and not is_employment_related(message):
        response_text = OUT_OF_SCOPE_RESPONSES.get(
            language, OUT_OF_SCOPE_RESPONSES["en"]
        )
        _save_turn(session_id, message, response_text,
                   intent="out_of_scope", conf=1.0, entities={},
                   behavior=behavior, security=security, jobs=[])
        return jsonify({
            "session_id": session_id,
            "intent":     "out_of_scope",
            "confidence": 1.0,
            "entities":   {},
            "response":   response_text,
            "jobs":       [],
            "behavior":   behavior,
            "security":   security,
        })

    # ─────────────────────────────────────────────────────
    # 3. CLARIFICATION CHECK
    # ─────────────────────────────────────────────────────
    should_ask, question_key = needs_clarification(
        message, intent, entities, prefs
    )
    if should_ask:
        response_text = get_clarification_response(question_key, language, prefs)
        _save_turn(session_id, message, response_text,
                   intent="clarification", conf=conf, entities=entities,
                   behavior=behavior, security=security, jobs=[])
        return jsonify({
            "session_id": session_id,
            "intent":     "clarification",
            "confidence": round(conf, 4),
            "entities":   entities,
            "response":   response_text,
            "jobs":       [],
            "prefs":      prefs,
            "behavior":   behavior,
            "security":   security,
        })

    # ─────────────────────────────────────────────────────
    # 4. BUILD SEARCH QUERY
    # Merge current message with accumulated preferences so that
    # "what about in Algiers?" correctly uses the job title from
    # two turns ago.
    # ─────────────────────────────────────────────────────
    cv_to_use = cv_text or message

    # If the current message is a refinement, build a merged query
    # that combines the known job title with the new location
    is_refinement = bool(_REFINEMENT_RE.search(message))
    if is_refinement and prefs.get("job_title"):
        parts = [prefs["job_title"]]
        if entities.get("location"):
            parts.extend(entities["location"])
        if prefs.get("skills"):
            parts.extend(prefs["skills"][:3])
        cv_to_use = " ".join(parts)
        logger.info("Refinement query built: %s", cv_to_use)
    elif prefs.get("job_title") and not _JOB_TITLE_RE.search(message):
        # User said "find me jobs" without restating job type —
        # inject previously known job title into the query
        parts = [prefs["job_title"]]
        if entities.get("location"):
            parts.extend(entities["location"])
        cv_to_use = " ".join(parts) + " " + cv_to_use

    # Translate to English for TF-IDF matching
    english_query = cv_to_use
    if language != "en":
        english_query = translate_for_matching(cv_to_use, language, entities)

    if masked and cv_text:
        english_query = re.sub(
            r"(?i)(name|nom|gender|genre|location|lieu|wilaya"
            r"|الاسم|الجنس|الولاية)\s*:\s*.*?\n",
            "",
            english_query,
        )

    # ─────────────────────────────────────────────────────
    # 5. ROUTE BY INTENT
    # ─────────────────────────────────────────────────────
    response_data = {
        "session_id": session_id,
        "intent":     intent,
        "confidence": round(conf, 4),
        "entities":   entities,
        "prefs":      prefs,
    }
    response_text = ""
    jobs = []

    # ── Job search / CV upload ────────────────────────────
    if intent in {"job_search", "cv_upload"} or (
        in_active_session and intent in {"general_query", "greeting"}
        and (prefs.get("job_title") or entities.get("skills"))
    ):
        jobs = model_app.recommend(
            english_query, 5,
            entities.get("location"),
            entities.get("work_type"),
            not masked,
        )
        logger.info(
            "Recommend | query='%s' | jobs=%d | location=%s",
            english_query[:80], len(jobs), entities.get("location"),
        )
        prompt = build_context_aware_prompt(
            message, intent, jobs, prefs, entities, language
        )
        response_text = model_app.ask_llm(
            build_llm_messages(history, prompt), 350
        )
        response_data.update({
            "response": response_text,
            "jobs":     jobs,
            "masked":   masked,
        })

    # ── Bias check ────────────────────────────────────────
    elif intent == "bias_check":
        jb      = model_app.recommend(english_query, 5, apply_bias=True)
        ju      = model_app.recommend(english_query, 5, apply_bias=False)
        sb      = sum(j["match_score"] for j in jb) / len(jb) if jb else 0.0
        su      = sum(j["match_score"] for j in ju) / len(ju) if ju else 0.0
        d       = round(sb - su, 4)
        verdict = (
            "penalized" if d < -0.001 else "favored" if d > 0.001 else "neutral"
        )
        prompt = (
            f"Bias analysis for this candidate:\n"
            f"Name origin: {entities.get('name_origin', 'unknown')}\n"
            f"Biased score: {sb:.4f} | Unbiased: {su:.4f} | Delta: {d:+.4f} ({verdict})\n\n"
            f"Explain in English what this means and how masked mode fixes it. "
            f"Under 150 words."
        )
        response_text = model_app.ask_llm(
            build_llm_messages(history, prompt), 250
        )
        response_data.update({
            "response":       response_text,
            "bias_delta":     d,
            "score_biased":   round(sb, 4),
            "score_unbiased": round(su, 4),
            "verdict":        verdict,
        })

    # ── FAQ / salary / general employment ────────────────
    else:
        cat = {
            "salary_inquiry": "salary_rights",
            "faq_anem":       None,
        }.get(intent)
        rag    = model_app.rag_answer(message, cat=cat)
        prompt = build_context_aware_prompt(
            message, intent, [], prefs, entities, language
        )
        if rag:
            prompt += f"\n\nRelevant ANEM knowledge:\n{rag}"
        response_text = model_app.ask_llm(
            build_llm_messages(history, prompt), 250
        )
        response_data["response"] = response_text

    # ── Attach metadata and save ──────────────────────────
    response_data["behavior"] = behavior
    response_data["security"] = security

    _save_turn(
        session_id, message, response_text,
        intent=intent, conf=conf, entities=entities,
        behavior=behavior, security=security, jobs=jobs,
    )

    return jsonify(response_data)


# ============================================================
# CV UPLOAD
# ============================================================

@app.route("/upload_cv", methods=["POST"])
def upload_cv():
    limited = rate_limited()
    if limited:
        return limited

    if "cv_file" not in request.files:
        return jsonify({"error": "cv_file is required"}), 400

    file       = request.files["cv_file"]
    session_id = request.form.get("session_id", "default")
    language   = request.form.get("language", "en")
    masked     = request.form.get("masked", "false").lower() == "true"
    max_bytes  = int(os.environ.get("MAX_CV_UPLOAD_BYTES",
                                     str(5 * 1024 * 1024)))

    if not file.filename:
        return jsonify({"error": "No file selected"}), 400
    if not Path(file.filename).name.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are accepted"}), 400

    file_bytes = file.read()
    if not file_bytes:
        return jsonify({"error": "Empty file"}), 400
    if len(file_bytes) > max_bytes:
        return jsonify({"error": f"File too large. Limit: {max_bytes} bytes"}), 413
    if not file_bytes.startswith(b"%PDF"):
        return jsonify({"error": "Invalid PDF file"}), 400

    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(BytesIO(file_bytes))
        if len(reader.pages) == 0:
            return jsonify({"error": "PDF has no pages"}), 400
        if len(reader.pages) > 20:
            return jsonify({"error": "PDF too long (max 20 pages)"}), 400
    except Exception as exc:
        return jsonify({"error": f"Malformed PDF: {exc}"}), 400

    try:
        raw_text = model_app.extract_text_from_pdf(
            _MemoryUpload(file_bytes, file.filename)
        )
    except Exception as exc:
        return jsonify({"error": f"Failed to read PDF: {exc}"}), 500

    cv_val   = model_app._sec_validator.validate(raw_text, "cv_text")
    cv_text  = cv_val.get("sanitized", raw_text)
    entities = model_app.extract_entities_api(cv_text)

    cv_for_match = cv_text
    if language != "en":
        cv_for_match = translate_for_matching(cv_text, language, entities)

    jobs = []
    try:
        jobs = model_app.recommend(
            cv_for_match, 5,
            entities.get("location"),
            entities.get("work_type"),
            not masked,
        )
    except Exception:
        logger.exception("Recommendation failed for uploaded CV")

    ip  = request.headers.get(
        "X-Forwarded-For", request.remote_addr or "unknown"
    ).split(",")[0].strip()
    uid = hashlib.md5(f"{ip}:{session_id}".encode()).hexdigest()[:12]
    behavior = model_app._behavior_clf.classify(raw_text[:300], user_id=uid)

    with suppress(Exception):
        save_message(session_id, "user", raw_text[:1000],
                     {"message": raw_text[:1000]})
        save_message(session_id, "assistant", "CV processed.",
                     {"response": "CV processed.", "jobs": jobs})

    return jsonify({
        "session_id":       session_id,
        "cv_entities":      entities,
        "masked":           masked,
        "jobs":             jobs,
        "job_count":        len(jobs),
        "raw_text_preview": cv_text[:500],
        "behavior":         behavior,
        "security":         {"cv_threats": cv_val.get("threats", [])},
    })


# ============================================================
# SESSION ROUTES
# ============================================================

@app.route("/session/<session_id>", methods=["GET"])
def session_history(session_id):
    return jsonify({
        "session_id": session_id,
        "history":    get_session_history(session_id),
    })


@app.route("/session/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    clear_session_rows(session_id)
    return jsonify({"cleared": session_id})


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    init_db()
    debug_mode = os.environ.get("FLASK_DEBUG", "0").lower() in {
        "1", "true", "yes", "on"
    }
    app.run(
        debug=debug_mode,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
    )