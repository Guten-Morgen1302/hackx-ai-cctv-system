"""
utils/report_builder.py
Builds text and PDF shift reports for SecureVista.
"""

from __future__ import annotations
import io
import datetime
from utils.fake_data import FAKE_INCIDENTS


def _shift_label(date: datetime.date) -> str:
    hour = datetime.datetime.now().hour
    if 6 <= hour < 12:
        return "Morning (06:00 - 12:00)"
    elif 12 <= hour < 20:
        return "Evening (12:00 - 20:00)"
    else:
        return "Night (20:00 - 06:00)"


def _ascii(text: str) -> str:
    """Replace common Unicode punctuation with ASCII equivalents for Courier-safe text."""
    return (
        text.replace("\u2013", "-")   # en-dash
            .replace("\u2014", "--")  # em-dash
            .replace("\u2019", "'")   # right single quote
            .replace("\u2018", "'")   # left single quote
            .replace("\u201c", '"')   # left double quote
            .replace("\u201d", '"')   # right double quote
            .replace("\u2026", "...")  # ellipsis
    )


def _report_summary(date: datetime.date) -> dict:
    """Build summary statistics from fake incidents."""
    incidents = FAKE_INCIDENTS
    total = len(incidents)
    critical = sum(1 for i in incidents if i["risk_tier"] == "CRITICAL")
    high = sum(1 for i in incidents if i["risk_tier"] == "HIGH")
    medium = sum(1 for i in incidents if i["risk_tier"] == "MEDIUM")
    low = total - critical - high - medium

    # Count event types
    type_counts: dict[str, int] = {}
    for inc in incidents:
        et = inc["event_type"]
        type_counts[et] = type_counts.get(et, 0) + 1
    sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)

    # Zone counts
    zone_counts: dict[str, int] = {}
    for inc in incidents:
        z = inc["zone"]
        zone_counts[z] = zone_counts.get(z, 0) + 1
    top_zone = max(zone_counts, key=zone_counts.__getitem__)

    return {
        "date": date.strftime("%Y-%m-%d"),
        "shift": _shift_label(date),
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": total,
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
        "top_types": sorted_types,
        "top_zone": top_zone,
        "top_zone_count": zone_counts[top_zone],
        "blockchain_anchored": 7,
        "voice_calls": 4,
        "response_rate": "91.6%",
        "incidents": incidents,
    }


def build_text_report(date: datetime.date) -> str:
    """Return a formatted Markdown text report string."""
    s = _report_summary(date)

    lines = [
        "```",
        "SecureVista Security Report",
        f"Date: {s['date']} | Shift: {s['shift']}",
        f"Generated: {s['generated']}",
        "-" * 45,
        f"Total Alerts    : {s['total']}",
        f"CRITICAL        : {s['critical']}",
        f"HIGH            : {s['high']}",
        f"MEDIUM          : {s['medium']}",
        f"LOW             : {s['low']}",
        "",
        "Top Incident Types:",
    ]
    for rank, (etype, count) in enumerate(s["top_types"], 1):
        lines.append(f"  {rank}. {etype:<22} - {count} incident{'s' if count > 1 else ''}")

    lines += [
        "",
        f"Highest Risk Zone: {s['top_zone']} ({s['top_zone_count']} alerts)",
        "",
        f"Blockchain Anchored Events: {s['blockchain_anchored']}",
        f"Voice Calls Triggered      : {s['voice_calls']}",
        f"Response Rate              : {s['response_rate']}",
        "",
        "-" * 45,
        "Incidents (Summary):",
        "-" * 45,
    ]

    for inc in s["incidents"]:
        tier_label = inc["risk_tier"]
        lines += [
            f"{inc['incident_id']}",
            f"  Type   : {inc['event_type']}",
            f"  Zone   : {inc['zone']}",
            f"  Tier   : {tier_label}",
            f"  Time   : {inc['timestamp']}",
            f"  Status : {inc['status']}",
            "  " + "-" * 40,
        ]

    lines += [
        "",
        "Powered by SecureVista AI Platform",
        "```",
    ]

    return "\n".join(lines)


def build_pdf_report(date: datetime.date) -> bytes:
    """Generate a PDF report using fpdf2.  Uses Helvetica (core font, always
    available) so it works on any machine without external TTF files."""
    try:
        from fpdf import FPDF  # type: ignore
    except ImportError:
        raise RuntimeError("fpdf2 is not installed. Run: pip install fpdf2")

    s = _report_summary(date)

    # Helvetica is a core PDF font — Latin-1 range only.
    # Strip / replace any chars outside that range.
    def _h(text: str) -> str:
        """Sanitise to Latin-1 safe string."""
        return (
            text.replace("\u2013", "-")    # en-dash
                .replace("\u2014", "--")   # em-dash
                .replace("\u2018", "'")    # left single quote
                .replace("\u2019", "'")    # right single quote
                .replace("\u201c", '"')    # left double quote
                .replace("\u201d", '"')    # right double quote
                .replace("\u2026", "...")  # ellipsis
                .replace("\u2500", "-")    # box-drawing horizontal
                .encode("latin-1", errors="replace")
                .decode("latin-1")
        )

    FONT = "Helvetica"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)

    def _cell(text: str, h: int = 6, bold: bool = False,
              size: int = 10, align: str = "L") -> None:
        pdf.set_font(FONT, "B" if bold else "", size)
        pdf.cell(0, h, _h(text), ln=True, align=align)

    # ── Header ────────────────────────────────────────────────────────────────
    pdf.set_text_color(30, 30, 30)
    _cell("SecureVista", h=12, bold=True, size=22, align="C")
    pdf.set_text_color(100, 100, 100)
    _cell("AI-Powered Security Operations Report", h=6, size=11, align="C")
    pdf.ln(4)

    # ── Red accent divider ────────────────────────────────────────────────────
    pdf.set_draw_color(220, 50, 50)
    pdf.set_line_width(0.8)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(5)

    # ── Meta ──────────────────────────────────────────────────────────────────
    pdf.set_text_color(50, 50, 50)
    _cell(f"Date: {s['date']}    Shift: {s['shift']}", size=10)
    _cell(f"Generated: {s['generated']}", size=10)
    pdf.ln(4)

    def _section_header(title: str) -> None:
        pdf.set_text_color(30, 30, 30)
        _cell(title, h=8, bold=True, size=12)
        pdf.set_draw_color(180, 180, 180)
        pdf.set_line_width(0.3)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(2)

    # ── Alert Summary ─────────────────────────────────────────────────────────
    _section_header("ALERT SUMMARY")
    for label, val in [
        ("Total Alerts", s["total"]),
        ("CRITICAL",     s["critical"]),
        ("HIGH",         s["high"]),
        ("MEDIUM",       s["medium"]),
        ("LOW",          s["low"]),
    ]:
        pdf.set_font(FONT, "", 10)
        pdf.cell(70, 6, f"  {label}", border=0)
        pdf.cell(0, 6, f": {val}", ln=True)
    pdf.ln(3)

    # ── Top Incident Types ────────────────────────────────────────────────────
    _section_header("TOP INCIDENT TYPES")
    for rank, (etype, count) in enumerate(s["top_types"], 1):
        pdf.set_font(FONT, "", 10)
        pdf.cell(0, 6, _h(f"  {rank}. {etype} - {count} incident{'s' if count > 1 else ''}"), ln=True)
    pdf.ln(3)

    # ── Key Metrics ───────────────────────────────────────────────────────────
    _section_header("KEY METRICS")
    for ln_text in [
        f"  Highest Risk Zone         : {s['top_zone']} ({s['top_zone_count']} alerts)",
        f"  Blockchain Anchored Events: {s['blockchain_anchored']}",
        f"  Voice Calls Triggered     : {s['voice_calls']}",
        f"  Response Rate             : {s['response_rate']}",
    ]:
        pdf.set_font(FONT, "", 10)
        pdf.cell(0, 6, _h(ln_text), ln=True)
    pdf.ln(4)

    # ── Incident Log ──────────────────────────────────────────────────────────
    _section_header("INCIDENT LOG")

    for inc in s["incidents"]:
        if pdf.get_y() > 252:
            pdf.add_page()
        # ID row — bold
        pdf.set_font(FONT, "B", 9)
        pdf.cell(0, 5, _h(inc["incident_id"]), ln=True)
        # Detail rows
        pdf.set_font(FONT, "", 9)
        pdf.cell(0, 5, _h(f"  Type: {inc['event_type']}   Zone: {inc['zone']}"), ln=True)
        pdf.cell(0, 5, _h(f"  Tier: {inc['risk_tier']}   Time: {inc['timestamp']}   Status: {inc['status']}"), ln=True)
        # Hairline separator
        pdf.set_draw_color(210, 210, 210)
        pdf.set_line_width(0.1)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(1.5)

    # ── Footer ────────────────────────────────────────────────────────────────
    pdf.set_y(-20)
    pdf.set_font(FONT, "I", 8)
    pdf.set_text_color(130, 130, 130)
    pdf.cell(0, 6, _h("Powered by SecureVista AI Platform - Confidential"), align="C")

    return bytes(pdf.output())

