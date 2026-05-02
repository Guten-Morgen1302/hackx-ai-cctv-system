"""
commands/who_is_inside.py
/who_is_inside — Lists people currently tracked inside (real DB or fake data).
"""

import logging
import sqlite3

from telegram import Update
from telegram.ext import ContextTypes

from config import DB_PATH
from utils.fake_data import FAKE_PERSONS_INSIDE

logger = logging.getLogger(__name__)

STATUS_EMOJI = {"MOVING": "🟢", "STANDING": "🟡", "STATIONARY": "🟠", "UNKNOWN": "⚪"}


def _load_from_db() -> list[dict] | None:
    """Try to load tracked persons from SQLite. Returns None if unavailable."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=3)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tracked_persons WHERE status != 'EXITED' ORDER BY entered_at DESC"
        )
        rows = cursor.fetchall()
        conn.close()
        if rows:
            return [dict(r) for r in rows]
    except Exception as e:
        logger.debug("DB unavailable (%s) — falling back to fake data", e)
    return None


async def who_is_inside_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /who_is_inside command."""
    persons = _load_from_db() or FAKE_PERSONS_INSIDE
    count = len(persons)

    lines = [f"👁️ *Currently Tracked — {count} Active ID{'s' if count != 1 else ''}*\n"]

    for p in persons:
        pid = p.get("id", "??")
        zone = p.get("zone", "UNKNOWN")
        status = p.get("status", "UNKNOWN")
        entered = p.get("entered_at", "??:??")[:5]   # trim seconds if present
        emoji = STATUS_EMOJI.get(status.upper(), "⚪")

        lines.append(
            f"ID `{str(pid).zfill(2)}` | `{zone:<17}` | {emoji} `{status:<8}` | since `{entered}`"
        )

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
