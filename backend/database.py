import json
import os
import sqlite3
import hashlib
from secrets import token_urlsafe
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(BASE_DIR, "data")
DEFAULT_DB_PATH = os.path.join(DATA_DIR, "wassit.db")


def get_db_path():
    path = os.environ.get("WASSIT_DB_PATH", DEFAULT_DB_PATH)
    if os.path.isabs(path):
        return path
    if path.startswith("backend/") or path.startswith("./backend/"):
        return os.path.abspath(os.path.join(ROOT_DIR, path))
    return os.path.abspath(os.path.join(BASE_DIR, path))


def ensure_parent_dir(path):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def connect():
    path = get_db_path()
    ensure_parent_dir(path)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def db_session():
    connection = connect()
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def init_db():
    with db_session() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                avatar_id TEXT DEFAULT 'orbit',
                bio TEXT,
                location TEXT,
                profession TEXT,
                website TEXT,
                preferences_json TEXT,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS auth_tokens (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                payload_json TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_chat_messages_session_created
                ON chat_messages(session_id, created_at);
            """
        )
        
        # Add profile_picture_path column if it doesn't exist (migration)
        try:
            connection.execute(
                """
                CREATE TABLE user_profiles_new (
                    user_id INTEGER PRIMARY KEY,
                    avatar_id TEXT DEFAULT 'orbit',
                    bio TEXT,
                    location TEXT,
                    profession TEXT,
                    website TEXT,
                    profile_picture_path TEXT,
                    preferences_json TEXT,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
        except sqlite3.OperationalError:
            # Table might already have the column, check by trying a simple query
            try:
                connection.execute("SELECT profile_picture_path FROM user_profiles LIMIT 1")
            except sqlite3.OperationalError:
                # Column doesn't exist, need to migrate
                connection.execute("ALTER TABLE user_profiles ADD COLUMN profile_picture_path TEXT")


def hash_password(password):
    salt = os.environ.get("PASSWORD_SALT", "wassit-salt")
    return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()


def create_user(full_name, email, password):
    with db_session() as connection:
        cursor = connection.execute(
            """
            INSERT INTO users(full_name, email, password_hash, created_at)
            VALUES(?, ?, ?, ?)
            """,
            (full_name, email.lower().strip(), hash_password(password), utc_now()),
        )
        return cursor.lastrowid


def get_user_by_email(email):
    with db_session() as connection:
        row = connection.execute(
            "SELECT id, full_name, email, password_hash, created_at FROM users WHERE email = ?",
            (email.lower().strip(),),
        ).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id):
    with db_session() as connection:
        row = connection.execute(
            "SELECT id, full_name, email, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def create_auth_token(user_id):
    token = token_urlsafe(32)
    with db_session() as connection:
        connection.execute(
            "INSERT INTO auth_tokens(token, user_id, created_at) VALUES(?, ?, ?)",
            (token, user_id, utc_now()),
        )
    return token


def get_user_by_token(token):
    with db_session() as connection:
        row = connection.execute(
            """
            SELECT u.id, u.full_name, u.email, u.created_at
            FROM auth_tokens t
            JOIN users u ON u.id = t.user_id
            WHERE t.token = ?
            """,
            (token,),
        ).fetchone()
    return dict(row) if row else None


def ensure_session(session_id):
    timestamp = utc_now()
    with db_session() as connection:
        connection.execute(
            """
            INSERT INTO chat_sessions(session_id, created_at, updated_at)
            VALUES(?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET updated_at=excluded.updated_at
            """,
            (session_id, timestamp, timestamp),
        )


def save_message(session_id, role, content, payload=None):
    ensure_session(session_id)
    payload_json = json.dumps(payload, ensure_ascii=False) if payload is not None else None
    with db_session() as connection:
        connection.execute(
            """
            INSERT INTO chat_messages(session_id, role, content, payload_json, created_at)
            VALUES(?, ?, ?, ?, ?)
            """,
            (session_id, role, content, payload_json, utc_now()),
        )
        connection.execute(
            "UPDATE chat_sessions SET updated_at=? WHERE session_id=?",
            (utc_now(), session_id),
        )


def get_history(session_id, limit=40):
    with db_session() as connection:
        rows = connection.execute(
            """
            SELECT role, content, payload_json, created_at
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY id ASC
            LIMIT ?
            """,
            (session_id, limit),
        ).fetchall()

    history = []
    for row in rows:
        payload = json.loads(row["payload_json"]) if row["payload_json"] else {}
        history.append(
            {
                "role": row["role"],
                "content": row["content"],
                "timestamp": row["created_at"],
                **payload,
            }
        )
    return history


def clear_session(session_id):
    with db_session() as connection:
        connection.execute("DELETE FROM chat_messages WHERE session_id=?", (session_id,))
        connection.execute("DELETE FROM chat_sessions WHERE session_id=?", (session_id,))


def get_user_profile(user_id):
    """Retrieve user profile by user_id. Returns dict or None."""
    with db_session() as connection:
        row = connection.execute(
            """
            SELECT user_id, avatar_id, bio, location, profession, website, profile_picture_path, preferences_json, updated_at
            FROM user_profiles
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()
    
    if row:
        profile = dict(row)
        profile['preferences'] = json.loads(profile['preferences_json']) if profile['preferences_json'] else {}
        del profile['preferences_json']
        return profile
    return None


def create_or_update_user_profile(user_id, avatar_id=None, bio=None, location=None, profession=None, website=None, preferences=None):
    """Create or update user profile."""
    preferences_json = json.dumps(preferences, ensure_ascii=False) if preferences else None
    
    with db_session() as connection:
        # Check if profile exists
        existing = connection.execute(
            "SELECT user_id FROM user_profiles WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        
        if existing:
            # Update
            updates = []
            params = []
            if avatar_id is not None:
                updates.append("avatar_id = ?")
                params.append(avatar_id)
            if bio is not None:
                updates.append("bio = ?")
                params.append(bio)
            if location is not None:
                updates.append("location = ?")
                params.append(location)
            if profession is not None:
                updates.append("profession = ?")
                params.append(profession)
            if website is not None:
                updates.append("website = ?")
                params.append(website)
            if preferences_json is not None:
                updates.append("preferences_json = ?")
                params.append(preferences_json)
            
            updates.append("updated_at = ?")
            params.append(utc_now())
            params.append(user_id)
            
            if len(updates) > 1:  # More than just updated_at
                query = f"UPDATE user_profiles SET {', '.join(updates)} WHERE user_id = ?"
                connection.execute(query, params)
        else:
            # Create new profile with defaults
            connection.execute(
                """
                INSERT INTO user_profiles(user_id, avatar_id, bio, location, profession, website, preferences_json, updated_at)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, avatar_id or 'orbit', bio, location, profession, website, preferences_json, utc_now()),
            )


def stats():
    with db_session() as connection:
        sessions = connection.execute("SELECT COUNT(*) AS count FROM chat_sessions").fetchone()["count"]
        messages = connection.execute("SELECT COUNT(*) AS count FROM chat_messages").fetchone()["count"]
        users = connection.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]
    return {"sessions": sessions, "messages": messages, "users": users}


def get_profile_pictures_dir():
    """Get the profile pictures directory, create if needed."""
    pics_dir = os.path.join(DATA_DIR, "profile_pictures")
    os.makedirs(pics_dir, exist_ok=True)
    return pics_dir


def save_profile_picture(user_id, file_data, filename):
    """
    Save a profile picture for a user.
    Returns the relative path to store in the database or None on error.
    """
    import uuid
    from pathlib import Path
    
    pics_dir = get_profile_pictures_dir()
    
    # Generate unique filename
    file_ext = Path(filename).suffix.lower()
    if not file_ext:
        file_ext = ".jpg"
    unique_filename = f"{user_id}_{uuid.uuid4().hex}{file_ext}"
    filepath = os.path.join(pics_dir, unique_filename)
    
    try:
        with open(filepath, "wb") as f:
            f.write(file_data)
        
        # Update database with the picture path
        relative_path = f"profile_pictures/{unique_filename}"
        with db_session() as connection:
            connection.execute(
                """
                UPDATE user_profiles
                SET profile_picture_path = ?, updated_at = ?
                WHERE user_id = ?
                """,
                (relative_path, utc_now(), user_id)
            )
        
        return relative_path
    except Exception as e:
        print(f"Error saving profile picture: {e}")
        return None
