import os, re, pickle, joblib, json, time, threading, hashlib, logging, unicodedata
from dotenv import load_dotenv
try:
    import numpy as np
except Exception:
    np = None
try:
    import pandas as pd
except Exception:
    pd = None
import tempfile
from collections import defaultdict, deque
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, g
from flask_cors import CORS
try:
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:
    cosine_similarity = None
try:
    from scipy.sparse import load_npz
except Exception:
    load_npz = None

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

for env_path in (
    os.path.join(CURRENT_DIR, ".env"),
    os.path.join(PROJECT_ROOT, "backend", ".env"),
    os.path.join(PROJECT_ROOT, ".env"),
):
    load_dotenv(dotenv_path=env_path)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
security_logger = logging.getLogger("anem.security")
behavior_logger = logging.getLogger("anem.behavior")

app = Flask(__name__)
CORS(app)

class TokenBucketRateLimiter:
    def __init__(self, capacity=20, refill_rate=2.0):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._buckets = {}
        self._lock = threading.Lock()
    
    def _refill(self, tokens, last_ts):
        now = time.time()
        elapsed = now - last_ts
        return min(self.capacity, tokens + elapsed * self.refill_rate), now
    
    def is_allowed(self, key):
        with self._lock:
            tokens, last_ts = self._buckets.get(key, (self.capacity, time.time()))
            tokens, last_ts = self._refill(tokens, last_ts)
            if tokens >= 1.0:
                self._buckets[key] = (tokens - 1.0, last_ts)
                return True, tokens - 1.0, 0.0
            wait = (1.0 - tokens) / self.refill_rate
            self._buckets[key] = (tokens, last_ts)
            return False, 0.0, round(wait, 2)
    
    def cleanup_stale(self, max_age=3600):
        now = time.time()
        with self._lock:
            self._buckets = {k: v for k, v in self._buckets.items() if now - v[1] < max_age}

class IPThrottler:
    MAX_REQUESTS_PER_MINUTE = 60
    MAX_REQUESTS_PER_HOUR = 500
    BLOCK_DURATION_SECONDS = 600
    
    def __init__(self):
        self._mw = defaultdict(deque)
        self._hw = defaultdict(deque)
        self._bl = {}
        self._lock = threading.Lock()
    
    def check(self, ip):
        with self._lock:
            now = time.time()
            if ip in self._bl:
                ua = self._bl[ip]
                if now < ua:
                    return False, f"ip_blocked:retry_in_{round(ua - now)}s"
                del self._bl[ip]
            mq = self._mw[ip]
            hq = self._hw[ip]
            while mq and mq[0] < now - 60:
                mq.popleft()
            while hq and hq[0] < now - 3600:
                hq.popleft()
            if len(mq) >= self.MAX_REQUESTS_PER_MINUTE:
                self._bl[ip] = now + self.BLOCK_DURATION_SECONDS
                return False, "rate_limit_per_minute"
            if len(hq) >= self.MAX_REQUESTS_PER_HOUR:
                self._bl[ip] = now + self.BLOCK_DURATION_SECONDS * 3
                return False, "rate_limit_per_hour"
            mq.append(now)
            hq.append(now)
            return True, "ok"

class BehavioralClassifier:
    AGITATION_SIGNALS = {"why isn't", "not working", "broken", "still not", "nothing works"}
    AGGRESSION_SIGNALS = {"stupid", "idiot", "shut up", "useless system", "hack", "garbage system"}
    DISTRESS_SIGNALS = {"desperate", "no hope", "last resort", "please help me", "i give up"}
    ANOMALY_PATTERNS = [r"(.{5,})\1{3,}", r"[^\w\s]{10,}", r"<[^>]{1,200}>", r"\{\{.{1,100}\}\}", r"';\s*--"]
    
    def __init__(self):
        self._re = [re.compile(p, re.IGNORECASE) for p in self.ANOMALY_PATTERNS]
        self._hist = defaultdict(lambda: deque(maxlen=20))
    
    def classify(self, text, user_id="anon"):
        if not isinstance(text, str) or not text.strip():
            return self._r("NORMAL", 0.0, [], user_id)
        tl = text.lower().strip()
        flags, scores = [], {}
        for sig in self.AGGRESSION_SIGNALS:
            if sig in tl:
                scores["AGGRESSIVE"] = min(scores.get("AGGRESSIVE", 0.4) + 0.2, 1.0)
                flags.append("aggression")
                break
        for sig in self.AGITATION_SIGNALS:
            if sig in tl:
                scores["AGITATED"] = min(scores.get("AGITATED", 0.3) + 0.15, 0.95)
                flags.append("agitation")
                break
        for sig in self.DISTRESS_SIGNALS:
            if sig in tl:
                scores["DISTRESSED"] = min(scores.get("DISTRESSED", 0.35) + 0.18, 0.95)
                flags.append("distress")
                break
        for i, p in enumerate(self._re):
            if p.search(text):
                scores["ANOMALOUS"] = min(scores.get("ANOMALOUS", 0.0) + 0.3, 1.0)
                flags.append(f"anomaly_{i}")
        clf, conf = (max(scores, key=scores.get), scores[max(scores, key=scores.get)]) if scores else ("NORMAL", 0.0)
        result = self._r(clf, conf, flags, user_id)
        if result["flagged"]:
            behavior_logger.warning("FLAG|user=%s class=%s conf=%.2f", user_id, clf, conf)
        return result
    
    @staticmethod
    def _r(clf, conf, flags, uid):
        return {
            "classification": clf,
            "confidence": round(conf, 3),
            "flags": flags,
            "flagged": clf != "NORMAL" and conf >= 0.4,
            "user_id": uid,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

class SecurityValidator:
    MAX_MSG = 4000
    MAX_CV = 20000
    PATTERNS = [
        (r"(?:\'|\")\s*(?:OR|AND)\s+", "sql_injection"),
        (r";\s*(?:DROP|DELETE|INSERT|UPDATE|EXEC)\s+", "sql_ddl"),
        (r"<script[\s>]", "xss_script"),
        (r"javascript\s*:", "xss_js"),
        (r"\.\.[/\\]", "path_traversal"),
        (r"\{\{.{0,100}\}\}", "template_injection"),
        (r"\x00", "null_byte")
    ]
    
    def __init__(self):
        self._c = [(re.compile(p, re.IGNORECASE), l) for p, l in self.PATTERNS]
    
    def validate(self, text, ctx="message"):
        if not isinstance(text, str):
            return {"sanitized": "", "threats": ["non_string"], "truncated": False}
        threats, truncated = [], False
        limit = self.MAX_CV if ctx == "cv_text" else self.MAX_MSG
        if len(text) > limit:
            text, truncated = text[:limit], True
            threats.append(f"oversized_{limit}")
        for pat, lbl in self._c:
            if pat.search(text):
                threats.append(lbl)
        s = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
        s = re.sub(r"<script[\s\S]*?</script>", "", s, flags=re.IGNORECASE)
        s = re.sub(r"<[^>]{0,500}>", "", s)
        return {"sanitized": s, "threats": threats, "truncated": truncated}

_chat_limiter = TokenBucketRateLimiter(capacity=20, refill_rate=2.0)
_upload_limiter = TokenBucketRateLimiter(capacity=5, refill_rate=0.1)
_ip_throttler = IPThrottler()
_behavior_clf = BehavioralClassifier()
_sec_validator = SecurityValidator()

def _cleanup_loop():
    while True:
        time.sleep(1800)
        _chat_limiter.cleanup_stale()
        _upload_limiter.cleanup_stale()

threading.Thread(target=_cleanup_loop, daemon=True).start()

def rate_limit(limiter):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
            allowed_ip, reason = _ip_throttler.check(ip)
            if not allowed_ip:
                return jsonify({"error": "Too many requests", "reason": reason, "code": 429}), 429
            key = f"{ip}:{request.endpoint}"
            allowed, remaining, retry_after = limiter.is_allowed(key)
            if not allowed:
                resp = jsonify({"error": "Rate limit exceeded", "retry_after": retry_after, "code": 429})
                resp.status_code = 429
                resp.headers["Retry-After"] = str(retry_after)
                return resp
            g.rate_limit_remaining = remaining
            return f(*args, **kwargs)
        return wrapper
    return decorator

print("Loading models (conditional)...")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_pkl(fn):
    artifact = resolve_artifact(fn)
    with open(artifact, "rb") as f:
        return pickle.load(f)

MODELS_DIR = os.path.join(BASE_DIR, "models")
ARCHIVE_DIR = os.path.join(BASE_DIR, "archive")

def resolve_artifact(*names):
    for name in names:
        for root in (MODELS_DIR, ARCHIVE_DIR):
            candidate = os.path.join(root, name)
            if os.path.exists(candidate):
                return candidate
    return None

def safe_joblib_load(fn):
    p = resolve_artifact(fn)
    if p and os.path.exists(p):
        try:
            return joblib.load(p)
        except Exception as e:
            logging.warning("Failed to load %s: %s", fn, e)
    else:
        logging.info("Model not present: %s", fn)
    return None

intent_pipeline = safe_joblib_load("intent_classifier.pkl")
job_vectorizer = safe_joblib_load("job_vectorizer.pkl")
rag_vectorizer = None
if os.path.exists(os.path.join(MODELS_DIR, "rag_vectorizer.pkl")):
    try:
        rag_vectorizer = load_pkl("rag_vectorizer.pkl")
    except Exception as e:
        logging.warning("Failed to load rag_vectorizer.pkl: %s", e)

extractor_config = {}
extractor_path = resolve_artifact("entity_extractor_config.json")
if extractor_path:
    try:
        with open(extractor_path, encoding="utf-8") as f:
            extractor_config = json.load(f)
    except Exception as e:
        logging.warning("Failed to load entity_extractor_config.json: %s", e)
else:
    logging.info("No entity_extractor_config.json found; using empty defaults")

df_chunks = None
chunks_path = resolve_artifact("rag_chunks.csv")
if pd is not None and chunks_path:
    try:
        df_chunks = pd.read_csv(chunks_path)
    except Exception as e:
        logging.warning("Failed to read rag_chunks.csv: %s", e)

chunk_matrix = None
chunk_matrix_path = resolve_artifact("rag_chunk_matrix.npz")
if load_npz is not None and chunk_matrix_path:
    try:
        chunk_matrix = load_npz(chunk_matrix_path)
    except Exception as e:
        logging.warning("Failed to load rag_chunk_matrix.npz: %s", e)

df_jobs = None
jobs_path = resolve_artifact("algerian_jobs_sample.csv.gz", "algerian_jobs_sample.csv")
if pd is not None and jobs_path:
    try:
        df_jobs = pd.read_csv(jobs_path)
    except Exception as e:
        logging.warning("Failed to read algerian_jobs_sample.csv: %s", e)

job_matrix = None
if job_vectorizer is not None and df_jobs is not None and not df_jobs.empty:
    try:
        job_matrix = job_vectorizer.transform(df_jobs.get("job_text_clean", pd.Series([""] * len(df_jobs))).fillna(""))
    except Exception as e:
        logging.warning("Failed to build job_matrix: %s", e)

WILAYAS = extractor_config.get("wilayas", [])
SKILL_KEYWORDS = extractor_config.get("skill_keywords", [])
EDUCATION_LEVELS = extractor_config.get("education_levels", {})
WORK_TYPES = extractor_config.get("work_types", {})
NAME_ORIGINS = extractor_config.get("name_origins", {})
USD_TO_DZD = 132.99
RURAL_WILAYAS = ["Adrar", "Tamanrasset", "Tindouf", "Illizi", "In Salah"]
URBAN_WILAYAS_L = ["Algiers", "Oran", "Constantine", "Annaba", "Setif", "Blida"]
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
groq_client = Groq(api_key=GROQ_API_KEY) if (GROQ_AVAILABLE and GROQ_API_KEY) else None
GROQ_MODEL = "llama-3.1-8b-instant"
sessions = {}

# ============================================================
# SYSTEM PROMPT — English only, recruitment only
# ============================================================
SYSTEM_PROMPT = """You are RequAI, an intelligent employment assistant 
for Algeria's National Employment Agency (ANEM).

STRICT RULES — follow every rule, no exceptions:
1. LANGUAGE: Always respond in English only. Never switch to Arabic, 
   French, or Darija — even if the user writes in those languages.
2. SCOPE: Only answer questions about:
   - Job search and vacancies in Algeria
   - CV writing and improvement
   - ANEM procedures and registration
   - Algerian labor law and salary information
   - Interview preparation
   - Bias detection in job recommendations
   If the question is about anything else, politely decline and redirect.
3. CLARIFICATION: If the user asks for jobs without specifying what kind,
   always ask: "What type of job are you looking for? 
   (e.g. software engineer, accountant, driver...)"
4. JOB RESULTS: When presenting jobs, always include:
   - Job title and company name
   - Location (wilaya)
   - Salary range in DZD if available
   - Match score
5. NO JOBS FOUND: If no jobs match, give practical advice:
   - Register at ANEM (emploi.anem.dz)
   - Try nearby wilayas
   - Suggest related job titles to search for
6. TONE: Professional, helpful, concise. No filler phrases.
   No repetition. Maximum 200 words per response.

Example of a GOOD response:
"Here are 3 matching jobs in Algiers:
1. Software Engineer at Mobilis — 80,000-120,000 DZD/month — 94% match
2. Web Developer at Djezzy — 60,000-90,000 DZD/month — 87% match
Tip: Register at ANEM to access more opportunities."

Example of a BAD response:
"Of course! I'd be happy to help you find a job!
Sure! Let me search for jobs! 
Great question! Jobs are important..."
"""

EMPLOYMENT_TOPIC_KEYWORDS = {
    # English
    "job", "jobs", "work", "employment", "career", "recruit", "recruitment",
    "hiring", "hire", "cv", "resume", "interview", "salary", "vacancy",
    "vacancies", "candidate", "application", "apply", "offer", "anem",
    "job search", "professional", "skill", "skills", "wilaya", "position",
    "opening", "role", "opportunity", "internship", "apprenticeship",
    "part-time", "full-time", "remote", "freelance", "contract",
    # French
    "emploi", "travail", "recrutement", "poste", "salaire", "candidat",
    "candidature", "entreprise", "offre", "contrat", "expérience",
    "formation", "diplôme", "compétence", "stage", "télétravail",
    # Arabic / Darija
    "وظيفة", "وظائف", "عمل", "خدمة", "شغل", "توظيف", "راتب",
    "سيرة ذاتية", "مقابلة", "فرصة عمل", "منصب", "أنام", "تدريب",
    "مهارة", "مهارات", "تخصص", "تكوين", "ولاية", "شركة",
    "مطور", "مبرمج", "محاسب", "طبيب", "مهندس", "أستاذ", "معلم",
}

def contains_job_keyword(text):
    """Check if text contains any job keyword"""
    if not isinstance(text, str):
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in JOB_KEYWORDS)

def ask_for_job_type():
    """Return the prompt asking user to specify job type"""
    return "What job are you looking for in Algeria? Please specify a job title (e.g., developer, accountant, driver, teacher, nurse, electrician, etc.)"

def get_out_of_scope_response():
    """Return the response for off-topic questions"""
    return "I am an Algerian employment assistant. I can only help with job search, CV preparation, interviews, salaries, and ANEM-related questions. What job are you looking for in Algeria?"

def extract_text_from_pdf(file_storage):
    text = ""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        file_storage.save(tmp.name)
        tp = tmp.name
    if PDFPLUMBER_AVAILABLE:
        try:
            with pdfplumber.open(tp) as pdf:
                for pg in pdf.pages:
                    t = pg.extract_text()
                    if t:
                        text += t + "\n"
            if text.strip():
                os.unlink(tp)
                return text.strip()
        except:
            pass
    if PYPDF2_AVAILABLE:
        try:
            with open(tp, "rb") as f:
                rd = PyPDF2.PdfReader(f)
                for pg in rd.pages:
                    t = pg.extract_text()
                    if t:
                        text += t + "\n"
        except Exception as e:
            os.unlink(tp)
            return f"ERROR:{e}"
    os.unlink(tp)
    return text.strip()

def expand_search_text(text, entities=None):
    """Simple text expansion - keep English only"""
    if not isinstance(text, str):
        return ""
    return text.strip()

def is_employment_related(text):
    """Check if question is job/recruitment related"""
    if not isinstance(text, str):
        return False
    tl = text.lower()
    # Check for job keywords
    if contains_job_keyword(tl):
        return True
    # Check for employment topics
    if any(keyword in tl for keyword in EMPLOYMENT_TOPIC_KEYWORDS):
        return True
    return False

def ask_llm(messages, max_tokens=400):
    if not groq_client:
        return "Job search service is currently unavailable. Please try again later."
    try:
        if not messages or messages[0].get("role") != "system":
            messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
        r = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"Service error: {e}"

def get_session(sid):
    if sid not in sessions:
        sessions[sid] = []
    return sessions[sid]

def build_llm_messages(history, user_msg):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend([{"role": item["role"], "content": item["content"]} for item in history[-20:]])
    messages.append({"role": "user", "content": user_msg})
    return messages

def extract_name_field(cv):
    m = re.search(r"(?i)(?:name|nom)\s*:\s*(.+)", cv)
    if m:
        return m.group(1).strip().lower()
    for line in cv.split("\n"):
        s = line.strip()
        if s and len(s.split()) <= 4:
            return s.lower()
    return ""

def inject_bias(scores, cv):
    b = scores.copy().astype(float)
    nf = extract_name_field(cv)
    tl = cv.lower()
    an = NAME_ORIGINS.get("arabic", [])
    fn = NAME_ORIGINS.get("french", [])
    bn = NAME_ORIGINS.get("berber", [])
    if any(n in nf for n in an):
        b *= 0.94
    elif any(n in nf for n in fn):
        b *= 1.04
    elif any(n in nf for n in bn):
        b *= 0.92
    if any(w.lower() in tl for w in RURAL_WILAYAS):
        b *= 0.91
    elif any(w.lower() in tl for w in URBAN_WILAYAS_L):
        b *= 1.02
    if "female" in tl:
        b *= 0.96
    return b

def parse_salary(s):
    try:
        s = str(s).strip().upper().replace("DZD/MONTH", "").replace("DZD", "").replace(" ", "")
        p = s.split("-")[0] if "-" in s else s
        if "K" in p:
            return float(p.replace("K", "")) * 1000 * USD_TO_DZD
        return float(p.replace(",", ""))
    except:
        return None

def recommend(cv_text, top_n=5, loc=None, wt=None, apply_bias=True):
    if job_vectorizer is None or job_matrix is None or df_jobs is None or df_jobs.empty:
        return []
    
    query_entities = extract_entities_api(cv_text)
    cv_text = expand_search_text(cv_text, query_entities)
    loc = loc or query_entities.get("location")
    wt = wt or query_entities.get("work_type")
    
    try:
        cv_vec = job_vectorizer.transform([cv_text])
        scores = cosine_similarity(cv_vec, job_matrix).flatten()
        
        if apply_bias:
            scores = inject_bias(scores, cv_text)
        
        mask = np.ones(len(df_jobs), dtype=bool)
        if loc:
            lm = df_jobs["location"].str.lower().isin([l.lower() for l in loc])
            if lm.sum() > 0:
                mask &= lm.values
        if wt:
            wm = df_jobs["Work Type"].str.lower().str.contains(wt, na=False)
            if wm.sum() > 0:
                mask &= wm.values
        
        f = scores.copy()
        f[~mask] = -1
        idx = [i for i in f.argsort()[-top_n:][::-1] if f[i] > 0]
        
        if not idx:
            return []
        
        jobs = df_jobs.iloc[idx].copy()
        jobs["match_score"] = scores[idx].round(4)
        jobs["salary_dzd"] = jobs["Salary Range"].apply(parse_salary)
        
        cols = ["Job Title", "Role", "location", "Company", "Work Type", "Experience", "skills", "Salary Range", "salary_dzd", "match_score"]
        if "algerian_salary_range" in df_jobs.columns:
            jobs["algerian_salary_range"] = df_jobs.iloc[idx]["algerian_salary_range"].values
            cols.append("algerian_salary_range")
        
        return jobs[cols].to_dict("records")
    except Exception as e:
        logging.error(f"Recommendation error: {e}")
        return []

def rag_answer(query, cat=None):
    if rag_vectorizer is None or chunk_matrix is None or df_chunks is None:
        return None
    try:
        qv = rag_vectorizer.transform([query])
        sc = cosine_similarity(qv, chunk_matrix).flatten()
        if cat:
            mk = df_chunks["category"] == cat
            sc[~mk] = 0
        idx = sc.argsort()[-2:][::-1]
        tc = df_chunks.iloc[idx][sc[idx] > 0.01]
        if len(tc) == 0:
            return None
        seen, u = [], set()
        for a in tc["answer"].tolist():
            if a not in u:
                seen.append(a)
                u.add(a)
        return " ".join(seen[:2])
    except Exception as e:
        logging.error(f"RAG answer error: {e}")
        return None

def extract_entities_api(text):
    t = text.lower()
    e = {}
    normalized_latin = unicodedata.normalize("NFKD", text.lower())
    normalized_latin = "".join(ch for ch in normalized_latin if not unicodedata.combining(ch))
    
    found = [w for w in WILAYAS if w.lower() in normalized_latin]
    if found:
        e["location"] = found
    
    for lv, kws in EDUCATION_LEVELS.items():
        if any(kw.lower() in t for kw in kws):
            e["education"] = lv
            break
    
    for wtp, kws in WORK_TYPES.items():
        if any(kw.lower() in t for kw in kws):
            e["work_type"] = wtp
            break
    
    skills = [s for s in SKILL_KEYWORDS if s.lower() in t]
    if skills:
        e["skills"] = skills
    
    return e

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "name": "RequAI — ANEM Job Assistant",
        "version": "4.0",
        "language": "English Only",
        "focus": "Algerian Employment & Recruitment",
        "routes": ["POST /chat", "POST /upload_cv", "POST /recommend", "GET /health"]
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "llm": "connected" if groq_client else "not configured",
        "jobs": len(df_jobs) if df_jobs is not None else 0,
        "chunks": len(df_chunks) if df_chunks is not None else 0,
        "language": "English Only",
        "focus": "Job/Recruitment Only"
    })

@app.route("/chat", methods=["POST"])
@rate_limit(_chat_limiter)
def chat():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
    session_id = data.get("session_id", "default")
    user_email = data.get("user_email")
    storage_key = user_email if user_email else session_id
    user_id = hashlib.md5(f"{ip}:{storage_key}".encode()).hexdigest()[:12]
    message = data.get("message", "")
    cv_text = data.get("cv_text", None)
    masked = data.get("masked", False)
    
    if not message:
        return jsonify({"error": "message is required"}), 400
    
    # Validate and sanitize input
    msg_val = _sec_validator.validate(message, "message")
    message = msg_val["sanitized"]
    
    cv_threats = []
    if cv_text:
        cv_val = _sec_validator.validate(cv_text, "cv_text")
        cv_text = cv_val["sanitized"]
        cv_threats = cv_val["threats"]
    
    behavior = _behavior_clf.classify(message, user_id=user_id)
    history = get_session(storage_key)
    
    # Check if question is employment related
    if not is_employment_related(message):
        response_text = get_out_of_scope_response()
        response_data = {
            "session_id": storage_key,
            "intent": "out_of_scope",
            "confidence": 1.0,
            "entities": {},
            "response": response_text,
            "behavior": behavior,
            "security": {"message_threats": msg_val["threats"], "cv_threats": cv_threats},
        }
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response_text})
        sessions[storage_key] = history[-20:]
        return jsonify(response_data)
    
    # Get intent
    intent = "general_query"
    conf = 0.0
    if intent_pipeline:
        try:
            intent = intent_pipeline.predict([message])[0]
            conf = float(intent_pipeline.predict_proba([message]).max())
        except Exception:
            pass
    
    entities = extract_entities_api(message)
    cv_to_use = cv_text or message
    
    if masked and cv_text:
        cv_to_use = re.sub(r"(?i)(name|nom|gender|genre|location|lieu|wilaya)\s*:\s*.*?\n", "", cv_to_use)
    
    response_data = {
        "session_id": storage_key,
        "intent": intent,
        "confidence": round(conf, 4),
        "entities": entities
    }
    
    # Handle job search
    if intent in ["job_search", "cv_upload"]:
        # Check if user specified a job type
        has_job_type = contains_job_keyword(message) or contains_job_keyword(cv_to_use)
        
        if not has_job_type and len(message.split()) < 10:
            # Ask user to specify job type
            response_text = ask_for_job_type()
            response_data.update({
                "response": response_text,
                "jobs": [],
                "masked": masked,
                "asking_for_job_type": True
            })
        else:
            # Search for jobs
            jobs = recommend(cv_to_use, 5, entities.get("location"), entities.get("work_type"), not masked)
            
            if jobs:
                jobs_list = "\n".join([f"{i+1}. {j['Job Title']} at {j['Company']} - {j['location']} ({int(j['match_score']*100)}% match)" for i, j in enumerate(jobs)])
                prompt = f"""User is looking for a job: "{message}"

Available jobs in Algeria:
{jobs_list}

Respond in English ONLY. List the jobs clearly with job title, company, location, and match percentage. Be concise and helpful. Ask if they want more details about any position."""
                answer = ask_llm(build_llm_messages(history, prompt), 400)
                response_data.update({"response": answer, "jobs": jobs, "masked": masked})
            else:
                location = entities.get("location", ["Algeria"])[0] if entities.get("location") else "Algeria"
                prompt = f"""User is looking for a job: "{message}"

No jobs found in {location} at the moment.

Give practical advice in English ONLY:
1. Register with ANEM (National Employment Agency) - anem.dz
2. Try nearby wilayas/departments
3. Check job sites: emploi.anem.dz, LinkedIn, Ouedkniss
4. Submit your CV directly to companies

Then ask: What specific job title are you interested in?"""
                answer = ask_llm(build_llm_messages(history, prompt), 350)
                response_data.update({"response": answer, "jobs": [], "masked": masked})
    else:
        # General job-related query
        rag = rag_answer(message, cat=None)
        prompt = f"""User question: "{message}"
Context information: {rag or 'No specific information available'}
Respond in English ONLY, focusing on Algerian employment. Be concise and helpful."""
        answer = ask_llm(build_llm_messages(history, prompt), 300)
        response_data["response"] = answer
    
    response_data["behavior"] = behavior
    response_data["security"] = {"message_threats": msg_val["threats"], "cv_threats": cv_threats}
    
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response_data.get("response", "")})
    sessions[storage_key] = history[-20:]
    
    return jsonify(response_data)

@app.route("/upload_cv", methods=["POST"])
@rate_limit(_upload_limiter)
def upload_cv():
    if "cv_file" not in request.files:
        return jsonify({"error": "cv_file is required"}), 400
    
    file = request.files["cv_file"]
    session_id = request.form.get("session_id", "default")
    user_email = request.form.get("user_email")
    masked = request.form.get("masked", "false").lower() == "true"
    storage_key = user_email if user_email else session_id
    
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400
    
    safe_fn = re.sub(r"[^a-zA-Z0-9._\- ]", "", file.filename)
    if not safe_fn.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files accepted"}), 400
    
    raw_text = extract_text_from_pdf(file)
    if raw_text.startswith("ERROR"):
        return jsonify({"error": raw_text}), 500
    
    tv = _sec_validator.validate(raw_text, "cv_text")
    raw_text = tv["sanitized"]
    ec = extract_entities_api(raw_text)
    
    # Check if CV has job type information
    has_job_type = contains_job_keyword(raw_text)
    
    if not has_job_type:
        # Ask user what job they want
        return jsonify({
            "session_id": storage_key,
            "cv_entities": ec,
            "masked": masked,
            "jobs": [],
            "job_count": 0,
            "needs_job_type": True,
            "message": "I've received your CV. What job are you looking for in Algeria? (e.g., developer, accountant, driver, teacher, etc.)",
            "raw_text_preview": raw_text[:200],
            "security": {"cv_threats": tv["threats"], "truncated": tv["truncated"]}
        })
    
    # Search for jobs based on CV
    cu = raw_text[:500]
    cb = "Name: Candidate_X\nLocation: Location_X\n" + raw_text[:500]
    jb = recommend(cu, 5, apply_bias=True)
    ju = recommend(cb, 5, apply_bias=False)
    sb = np.mean([j["match_score"] for j in jb]) if jb else 0
    su = np.mean([j["match_score"] for j in ju]) if ju else 0
    d = round(sb - su, 4)
    
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
    uid = hashlib.md5(f"{ip}:{storage_key}".encode()).hexdigest()[:12]
    behavior = _behavior_clf.classify(raw_text[:300], user_id=uid)
    
    return jsonify({
        "session_id": storage_key,
        "cv_entities": ec,
        "masked": masked,
        "jobs": jb if not masked else ju,
        "job_count": len(jb),
        "bias_analysis": {
            "score_biased": round(sb, 4),
            "score_unbiased": round(su, 4),
            "delta": d,
            "verdict": "penalized" if d < -0.001 else "favored" if d > 0.001 else "neutral"
        },
        "raw_text_preview": raw_text[:200],
        "behavior": behavior,
        "security": {"cv_threats": tv["threats"], "truncated": tv["truncated"]}
    })

@app.route("/recommend", methods=["POST"])
@rate_limit(_chat_limiter)
def recommend_endpoint():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    cv = data.get("cv_text", "")
    if not cv:
        return jsonify({"error": "cv_text required"}), 400
    
    val = _sec_validator.validate(cv, "cv_text")
    cv = val["sanitized"]
    masked = data.get("masked", False)
    
    if masked:
        cv = re.sub(r"(?i)(name|nom|gender|genre|location|lieu|wilaya)\s*:\s*.*?\n", "", cv)
    
    jobs = recommend(cv, data.get("top_n", 5), data.get("location"), data.get("work_type"), not masked)
    
    return jsonify({
        "masked": masked,
        "count": len(jobs),
        "jobs": jobs,
        "security": {"threats": val["threats"]}
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))