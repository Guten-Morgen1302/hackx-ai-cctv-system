"""
commands/zone_status.py
/zone_status — Shows live risk levels per zone with randomised low-risk variation.
"""

import datetime
from telegram import Update
from telegram.ext import ContextTypes

from utils.fake_data import get_zone_status_live


async def zone_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /zone_status command."""
    zones = get_zone_status_live()
    now = datetime.datetime.now().strftime("%H:%M:%S")

    lines = [
        f"🛡️ *SecureVista — Zone Risk Status*",
        f"_Updated: {now}_\n",
    ]

    for z in zones:
        emoji = z["emoji"]
        zone  = z["zone"]
        level = z["level"]
        note  = z["note"]
        lines.append(f"{emoji} `{zone:<20}` — *{level:<8}* _{note}_")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
