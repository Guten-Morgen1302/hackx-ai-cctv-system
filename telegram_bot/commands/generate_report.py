"""
commands/generate_report.py
/generate_report [today | yesterday | date YYYY-MM-DD]
Sends a format picker keyboard, then generates text or PDF report.
"""

import datetime
import io
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils.report_builder import build_text_report, build_pdf_report

logger = logging.getLogger(__name__)


def _parse_date(args: list[str]) -> datetime.date:
    """Parse optional date argument, defaulting to today."""
    today = datetime.date.today()
    if not args:
        return today
    arg = args[0].lower()
    if arg == "today":
        return today
    if arg == "yesterday":
        return today - datetime.timedelta(days=1)
    if arg == "date" and len(args) >= 2:
        try:
            return datetime.date.fromisoformat(args[1])
        except ValueError:
            pass
    # Try parsing directly
    try:
        return datetime.date.fromisoformat(args[0])
    except ValueError:
        return today


async def generate_report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /generate_report command — show format picker."""
    date = _parse_date(context.args or [])
    # Store the date in user_data for the callback
    context.user_data["report_date"] = date.isoformat()

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📋 Text Report", callback_data=f"report_text_{date.isoformat()}"),
            InlineKeyboardButton("📕 PDF Report",  callback_data=f"report_pdf_{date.isoformat()}"),
        ]
    ])

    await update.message.reply_text(
        f"📄 *Generate Shift Report* — `{date.isoformat()}`\n\nChoose report format:",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


async def report_format_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Text / PDF report format selection callback."""
    query = update.callback_query
    await query.answer()

    data = query.data or ""

    if data.startswith("report_text_"):
        date_str = data.replace("report_text_", "")
        date = datetime.date.fromisoformat(date_str)
        await query.edit_message_text(
            "⏳ Generating text report…", parse_mode="Markdown"
        )
        try:
            report_text = build_text_report(date)
            # Send as a new message (may exceed edit limit)
            await query.message.reply_text(report_text, parse_mode="Markdown")
            await query.edit_message_text(
                f"✅ *Text report for `{date_str}` sent above.*", parse_mode="Markdown"
            )
        except Exception as e:
            logger.exception("Text report generation failed")
            await query.edit_message_text(f"⚠️ Report error: `{e}`", parse_mode="Markdown")

    elif data.startswith("report_pdf_"):
        date_str = data.replace("report_pdf_", "")
        date = datetime.date.fromisoformat(date_str)
        await query.edit_message_text(
            "⏳ Generating PDF report…", parse_mode="Markdown"
        )
        try:
            pdf_bytes = build_pdf_report(date)
            filename = f"SecureVista_Report_{date_str}.pdf"
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_file.name = filename
            await query.message.reply_document(
                document=pdf_file,
                filename=filename,
                caption=f"📕 *SecureVista Shift Report — {date_str}*",
                parse_mode="Markdown",
            )
            await query.edit_message_text(
                f"✅ *PDF report for `{date_str}` sent above.*", parse_mode="Markdown"
            )
        except Exception as e:
            logger.exception("PDF report generation failed")
            await query.edit_message_text(f"⚠️ PDF error: `{e}`", parse_mode="Markdown")
