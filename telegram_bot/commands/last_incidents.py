"""
commands/last_incidents.py
/last_incidents — Shows the last 10 security incidents (real DB or fake data).
"""

import logging
import sqlite3

from telegram import Update
from telegram.ext import ContextTypes

from config import DB_PATH
from utils.fake_data import FAKE_INCIDENTS

logger = logging.getLogger(__name__)

TIER_EMOJI = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}


def _load_from_db(limit: int = 10) -> list[dict] | None:
    """Try to load incidents from the SQLite DB. Returns None if unavailable."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=3)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM incidents ORDER BY timestamp DESC LIMIT ?", (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        if rows:
            return [dict(r) for r in rows]
    except Exception as e:
        logger.debug("DB unavailable: %s — falling back to fake data", e)
    return None


def _format_incident(inc: dict) -> str:
    tier = inc.get("risk_tier", "UNKNOWN")
    emoji = TIER_EMOJI.get(tier, "⚪")
    return (
        f"{emoji} `{inc.get('incident_id', 'N/A')}`\n"
        f"Type  : `{inc.get('event_type', 'UNKNOWN')}`\n"
        f"Zone  : `{inc.get('zone', 'N/A')}`\n"
        f"Tier  : `{tier}`\n"
        f"Time  : `{inc.get('timestamp', 'N/A')}`\n"
        f"Status: `{inc.get('status', 'N/A')}`\n"
        f"──────────────────"
    )


async def last_incidents_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /last_incidents command."""
    incidents = _load_from_db() or FAKE_INCIDENTS[:10]

    source = "🗄️ _Live DB_" if _load_from_db() else "📋 _Demo data_"
    header = f"🚨 *Last {len(incidents)} Security Incidents* {source}\n\n"

    text = header + "\n".join(_format_incident(i) for i in incidents)

    # Telegram message limit is 4096 chars; split if needed
    if len(text) > 4000:
        text = text[:4000] + "\n`... (truncated)`"

    await update.message.reply_text(text, parse_mode="Markdown")
