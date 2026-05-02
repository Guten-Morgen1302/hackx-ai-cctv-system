"""
commands/test_alert.py
/test_alert — Fires a fake CRITICAL FALL_DETECTED alert with inline action buttons.
"""

import secrets
import datetime
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from config import GUARD_PHONE

logger = logging.getLogger(__name__)


async def test_alert_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /test_alert command — fire a fake critical alert."""
    now = datetime.datetime.now().strftime("%H:%M:%S")
    fake_hash = "0x" + secrets.token_hex(6) + "..."
    # unique incident ID per call
    inc_id = f"INC-TEST-{datetime.datetime.now().strftime('%H%M%S')}"

    text = (
        f"🚨 *\\[SECUREVISTA CRITICAL ALERT\\]*\n\n"
        f"`Type      : FALL_DETECTED`\n"
        f"`Zone      : Hostel Corridor B`\n"
        f"`Risk Tier : 🔴 CRITICAL`\n"
        f"`Time      : {now}`\n"
        f"`Track ID  : 11`\n\n"
        f"⚠️ Person on floor without movement for 10 seconds\\.\n\n"
        f"*Action Required:*\n"
        f"  → Send guard to Hostel Corridor B immediately\n"
        f"  → Check camera feed on dashboard\n\n"
        f"`[Blockchain Log] Evidence anchored: {fake_hash}`\n"
        f"📞 Voice call scheduled → `{GUARD_PHONE}` in 15 seconds\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"*Respond:*"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Acknowledge", callback_data=f"ack_{inc_id}"),
            InlineKeyboardButton("🚨 Escalate",   callback_data=f"escalate_{inc_id}"),
        ],
        [
            InlineKeyboardButton("📸 View Snapshot", callback_data="snapshot_11"),
        ],
    ])

    await update.message.reply_text(
        text, parse_mode="MarkdownV2", reply_markup=keyboard
    )


async def alert_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button presses from test_alert messages."""
    query = update.callback_query
    await query.answer()

    data = query.data or ""
    user = query.from_user
    username = f"@{user.username}" if user.username else user.first_name
    now = datetime.datetime.now().strftime("%H:%M:%S")

    original = query.message.text or ""

    if data.startswith("ack_"):
        addition = f"\n\n✅ *Acknowledged* by {username} at `{now}`"
    elif data.startswith("escalate_"):
        addition = f"\n\n🚨 *Escalated* by {username} — Supervisor notified\\."
    elif data.startswith("snapshot_"):
        track_id = data.split("_", 1)[1]
        addition = f"\n\n📸 _Snapshot requested for Track ID {track_id}\\. Use /live\\_snapshot {track_id}_"
    else:
        return

    try:
        await query.edit_message_text(
            original + addition,
            parse_mode="MarkdownV2",
            reply_markup=None,
        )
    except Exception as e:
        logger.warning("Could not edit alert message: %s", e)
        await query.message.reply_text(addition.strip(), parse_mode="MarkdownV2")
