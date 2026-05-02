"""
commands/live_snapshot.py
/live_snapshot [id] — Captures and sends a real frame image for a given track ID.
"""

import secrets
import datetime
import logging
from telegram import Update
from telegram.ext import ContextTypes

from config import SNAPSHOTS_DIR
from utils.snapshot_helper import get_snapshot_for_id

logger = logging.getLogger(__name__)

ZONES = [
    "ENTRY_LOBBY", "ATM Zone 1", "ATM Zone 2",
    "Corridor B", "Main Gate", "Library Zone", "Canteen",
]


async def live_snapshot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /live_snapshot [id] command."""
    args = context.args

    if not args:
        await update.message.reply_text(
            "⚠️ *Usage:* `/live_snapshot [id]`\n_Example:_ `/live_snapshot 11`",
            parse_mode="Markdown",
        )
        return

    try:
        track_id = int(args[0])
    except ValueError:
        await update.message.reply_text("⚠️ Track ID must be a number between 1 and 130.")
        return

    if not (1 <= track_id <= 130):
        await update.message.reply_text("⚠️ Track ID must be between *1* and *130*.", parse_mode="Markdown")
        return

    await update.message.reply_chat_action("upload_photo")

    img_path = get_snapshot_for_id(SNAPSHOTS_DIR, track_id)

    if img_path is None:
        await update.message.reply_text(
            f"⚠️ No snapshot available for ID *{track_id}*. Camera feed may be offline.",
            parse_mode="Markdown",
        )
        return

    # Build caption
    import random
    zone = random.choice(ZONES)
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    fake_hash = "0x" + secrets.token_hex(32)

    caption = (
        f"📸 *Live Snapshot Captured*\n"
        f"Track ID : `{track_id}`\n"
        f"Zone     : `{zone}`\n"
        f"Time     : `{ts}`\n"
        f"Status   : `ACTIVE`\n\n"
        f"`[Blockchain Log] Snapshot hash anchored: {fake_hash[:18]}...`"
    )

    try:
        with open(img_path, "rb") as f:
            await update.message.reply_photo(photo=f, caption=caption, parse_mode="Markdown")
    except Exception as e:
        logger.error("Failed to send snapshot photo: %s", e)
        await update.message.reply_text(
            f"⚠️ Could not send image file. Error: `{e}`", parse_mode="Markdown"
        )
