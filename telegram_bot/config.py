"""
SecureVista Telegram Bot — Configuration
Reads all settings from .env file via python-dotenv.
"""

import os
from dotenv import load_dotenv

# Load .env from the telegram_bot directory
_env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(_env_path)

# ─── Core ────────────────────────────────────────────────────────────────────
BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Authorized chat IDs (comma-separated in .env)
_raw_ids = os.getenv("ALLOWED_CHAT_IDS", "")
ALLOWED_CHAT_IDS: list[int] = [
    int(x.strip()) for x in _raw_ids.split(",") if x.strip().lstrip("-").isdigit()
]

# ─── Paths ───────────────────────────────────────────────────────────────────
_base_dir = os.path.dirname(os.path.abspath(__file__))

SNAPSHOTS_DIR: str = os.path.normpath(
    os.path.join(_base_dir, os.getenv("SNAPSHOTS_DIR", "../logs/object_frames"))
)

DB_PATH: str = os.path.normpath(
    os.path.join(_base_dir, os.getenv("DB_PATH", "../securevista.db"))
)

ACCESS_LOG: str = os.path.join(_base_dir, "access.log")
ERROR_LOG: str = os.path.join(_base_dir, "error.log")

# ─── External services ───────────────────────────────────────────────────────
GUARD_PHONE: str = os.getenv("GUARD_PHONE", "+918169803818")
BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8080")
