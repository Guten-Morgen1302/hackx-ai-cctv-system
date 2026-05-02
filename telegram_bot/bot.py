"""
bot.py — SecureVista Telegram Bot
Main entry point. Wires all command handlers, auth middleware, and error logging.

Run:
    python bot.py
"""

import logging
import traceback
import datetime
import sys
import os

from telegram import Update, BotCommand
from telegram.request import HTTPXRequest
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ── Ensure telegram_bot/ is on the path when run directly ─────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    BOT_TOKEN,
    ALLOWED_CHAT_IDS,
    ACCESS_LOG,
    ERROR_LOG,
)

# ── Command handlers ───────────────────────────────────────────────────────────
from commands.live_snapshot  import live_snapshot_handler
from commands.last_incidents import last_incidents_handler
from commands.who_is_inside  import who_is_inside_handler
from commands.zone_status    import zone_status_handler
from commands.health         import health_handler
from commands.test_alert     import test_alert_handler, alert_callback_handler
from commands.generate_report import generate_report_handler, report_format_callback

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("SecureVista")

# Silence noisy httpx / telegram library logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)


# ── Auth guard ─────────────────────────────────────────────────────────────────
def _is_authorized(chat_id: int) -> bool:
    """Return True if chat_id is in the whitelist (or list is empty = open)."""
    if not ALLOWED_CHAT_IDS:
        return True  # No restriction configured — allow all (dev mode)
    return chat_id in ALLOWED_CHAT_IDS


def _log_unauthorized(chat_id: int, username: str, command: str) -> None:
    """Append unauthorized access attempt to access.log."""
    ts = datetime.datetime.now().isoformat()
    entry = f"[{ts}] UNAUTHORIZED | chat_id={chat_id} | user={username} | cmd={command}\n"
    try:
        with open(ACCESS_LOG, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass
    logger.warning("Unauthorized: chat_id=%s user=%s cmd=%s", chat_id, username, command)


def _log_error(error_text: str) -> None:
    """Append error to error.log."""
    ts = datetime.datetime.now().isoformat()
    try:
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{ts}]\n{error_text}\n{'─'*60}\n")
    except Exception:
        pass


# ── Middleware wrapper ─────────────────────────────────────────────────────────
def auth_wrap(handler):
    """
    Decorator factory: wraps any async command handler with:
      1. Authorization check
      2. try/except with error logging
    """
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        user = update.effective_user
        if chat is None:
            return

        chat_id = chat.id
        username = (user.username or user.first_name) if user else "unknown"
        command = (update.message.text or "").split()[0] if update.message else "unknown"

        if not _is_authorized(chat_id):
            _log_unauthorized(chat_id, username, command)
            await update.message.reply_text(
                "🔒 Unauthorized access\\. This incident has been logged\\.",
                parse_mode="MarkdownV2",
            )
            return

        try:
            await handler(update, context)
        except Exception:
            tb = traceback.format_exc()
            _log_error(f"Handler: {handler.__name__}\nChat: {chat_id}\n{tb}")
            logger.error("Error in %s:\n%s", handler.__name__, tb)
            try:
                await update.message.reply_text(
                    "⚠️ SecureVista encountered an internal error\\. Please try again\\.",
                    parse_mode="MarkdownV2",
                )
            except Exception:
                pass

    wrapped.__name__ = handler.__name__
    return wrapped


def auth_wrap_callback(handler):
    """Auth wrapper for CallbackQuery handlers (no message.reply_text)."""
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        chat = update.effective_chat
        user = update.effective_user

        if chat is None:
            return

        chat_id = chat.id
        username = (user.username or user.first_name) if user else "unknown"
        data = query.data if query else "unknown"

        if not _is_authorized(chat_id):
            _log_unauthorized(chat_id, username, f"callback:{data}")
            await query.answer("🔒 Unauthorized.", show_alert=True)
            return

        try:
            await handler(update, context)
        except Exception:
            tb = traceback.format_exc()
            _log_error(f"Callback handler: {handler.__name__}\nChat: {chat_id}\n{tb}")
            logger.error("Error in callback %s:\n%s", handler.__name__, tb)
            try:
                await query.answer("⚠️ Internal error. Please try again.", show_alert=True)
            except Exception:
                pass

    wrapped.__name__ = handler.__name__
    return wrapped


# ── /start command ─────────────────────────────────────────────────────────────
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome message."""
    text = (
        "🛡️ *SecureVista Security Bot* — Online\n\n"
        "🔴 *Authorized Access Only*\n"
        "`SOC Tier: Active | Node: ai-cctv-01`\n\n"
        "*Commands:*\n"
        "`/live_snapshot [id]`     — Capture frame for person ID\n"
        "`/last_incidents`         — Last 10 security incidents\n"
        "`/who_is_inside`          — People currently tracked inside\n"
        "`/zone_status`            — Zone risk levels live\n"
        "`/health`                 — System health check\n"
        "`/test_alert`             — Fire a test critical alert\n"
        "`/generate_report`        — Generate shift report \\(PDF or text\\)"
    )
    await update.message.reply_text(text, parse_mode="MarkdownV2")


# ── Global error handler ───────────────────────────────────────────────────────
async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    tb = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_str = "".join(tb)
    _log_error(f"Global error:\n{tb_str}")
    logger.error("Unhandled exception:\n%s", tb_str)


# ── Bot commands menu ──────────────────────────────────────────────────────────
BOT_COMMANDS = [
    BotCommand("start",           "SecureVista — show command list"),
    BotCommand("live_snapshot",   "Capture live frame for a track ID"),
    BotCommand("last_incidents",  "Show last 10 security incidents"),
    BotCommand("who_is_inside",   "List currently tracked persons"),
    BotCommand("zone_status",     "Live zone risk levels"),
    BotCommand("health",          "System health check"),
    BotCommand("test_alert",      "Fire a test CRITICAL alert"),
    BotCommand("generate_report", "Generate shift report (PDF or text)"),
]


# ── Main ───────────────────────────────────────────────────────────────────────
def main() -> None:
    if not BOT_TOKEN:
        logger.critical(
            "TELEGRAM_BOT_TOKEN is not set. "
            "Copy .env.example → .env and fill in your token."
        )
        sys.exit(1)

    logger.info("🛡️  SecureVista Bot starting…")
    logger.info("Snapshots dir : %s", os.path.abspath(
        __import__("config").SNAPSHOTS_DIR
    ))
    logger.info("Allowed chats : %s", ALLOWED_CHAT_IDS or "ALL (open mode)")

    # Longer timeouts for slow/congested networks
    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0,
    )
    app = Application.builder().token(BOT_TOKEN).request(request).build()

    # Register /start (no auth guard — anyone can see the splash)
    app.add_handler(CommandHandler("start", auth_wrap(start_handler)))

    # Register all protected commands
    app.add_handler(CommandHandler("live_snapshot",   auth_wrap(live_snapshot_handler)))
    app.add_handler(CommandHandler("last_incidents",  auth_wrap(last_incidents_handler)))
    app.add_handler(CommandHandler("who_is_inside",   auth_wrap(who_is_inside_handler)))
    app.add_handler(CommandHandler("zone_status",     auth_wrap(zone_status_handler)))
    app.add_handler(CommandHandler("health",          auth_wrap(health_handler)))
    app.add_handler(CommandHandler("test_alert",      auth_wrap(test_alert_handler)))
    app.add_handler(CommandHandler("generate_report", auth_wrap(generate_report_handler)))

    # Inline button callbacks
    app.add_handler(CallbackQueryHandler(
        auth_wrap_callback(alert_callback_handler),
        pattern=r"^(ack_|escalate_|snapshot_)"
    ))
    app.add_handler(CallbackQueryHandler(
        auth_wrap_callback(report_format_callback),
        pattern=r"^report_(text|pdf)_"
    ))

    # Global error handler
    app.add_error_handler(global_error_handler)

    # Set bot commands in Telegram UI
    async def post_init(application: Application) -> None:
        await application.bot.set_my_commands(BOT_COMMANDS)
        logger.info("✅ Bot commands menu registered.")

    app.post_init = post_init

    logger.info("✅ Bot is live and polling for commands.")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
