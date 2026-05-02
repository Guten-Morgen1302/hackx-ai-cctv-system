"""
utils/fake_data.py — Hardcoded realistic fake data for demo mode.
Used whenever the real SQLite DB is unavailable.
"""

import random

# ─── Incidents ────────────────────────────────────────────────────────────────
FAKE_INCIDENTS = [
    {
        "incident_id": "INC-2026-05-02-0012",
        "event_type": "FALL_DETECTED",
        "zone": "Hostel Corridor B",
        "risk_tier": "CRITICAL",
        "timestamp": "2026-05-02 19:41:03",
        "status": "ESCALATED",
    },
    {
        "incident_id": "INC-2026-05-02-0011",
        "event_type": "ABANDONED_OBJECT",
        "zone": "ATM Zone 1",
        "risk_tier": "HIGH",
        "timestamp": "2026-05-02 18:52:18",
        "status": "ACKNOWLEDGED",
    },
    {
        "incident_id": "INC-2026-05-02-0010",
        "event_type": "SHADOW_DETECTED",
        "zone": "Main Gate Cam 4",
        "risk_tier": "HIGH",
        "timestamp": "2026-05-02 18:31:44",
        "status": "ACKNOWLEDGED",
    },
    {
        "incident_id": "INC-2026-05-02-0009",
        "event_type": "LOITERING",
        "zone": "ATM Zone 2",
        "risk_tier": "MEDIUM",
        "timestamp": "2026-05-02 17:22:10",
        "status": "AUTO_RESOLVED",
    },
    {
        "incident_id": "INC-2026-05-02-0008",
        "event_type": "UPI_FRAUD",
        "zone": "ATM Zone 1",
        "risk_tier": "CRITICAL",
        "timestamp": "2026-05-02 16:45:09",
        "status": "BLOCKED",
    },
    {
        "incident_id": "INC-2026-05-02-0007",
        "event_type": "CROSS_DOMAIN",
        "zone": "ATM Zone 1",
        "risk_tier": "CRITICAL",
        "timestamp": "2026-05-02 16:44:52",
        "status": "ESCALATED",
    },
    {
        "incident_id": "INC-2026-05-02-0006",
        "event_type": "WEAPON_DETECTED",
        "zone": "Entry Gate Cam 1",
        "risk_tier": "CRITICAL",
        "timestamp": "2026-05-02 15:10:28",
        "status": "ESCALATED",
    },
    {
        "incident_id": "INC-2026-05-02-0005",
        "event_type": "SILENT_SOS",
        "zone": "Hostel Corridor A",
        "risk_tier": "CRITICAL",
        "timestamp": "2026-05-02 14:07:55",
        "status": "RESPONDED",
    },
    {
        "incident_id": "INC-2026-05-02-0004",
        "event_type": "FALL_DETECTED",
        "zone": "Library Exit",
        "risk_tier": "HIGH",
        "timestamp": "2026-05-02 13:52:30",
        "status": "RESOLVED",
    },
    {
        "incident_id": "INC-2026-05-02-0003",
        "event_type": "ABANDONED_OBJECT",
        "zone": "Canteen Entry",
        "risk_tier": "HIGH",
        "timestamp": "2026-05-02 12:31:11",
        "status": "RESOLVED",
    },
]

# ─── Tracked persons ──────────────────────────────────────────────────────────
FAKE_PERSONS_INSIDE = [
    {"id": 4,  "zone": "ENTRY_LOBBY",  "status": "MOVING",   "entered_at": "19:32:01"},
    {"id": 7,  "zone": "ATM Zone 1",   "status": "STANDING", "entered_at": "19:44:15"},
    {"id": 11, "zone": "Corridor B",   "status": "MOVING",   "entered_at": "20:01:33"},
    {"id": 16, "zone": "ENTRY_LOBBY",  "status": "STANDING", "entered_at": "19:55:22"},
    {"id": 18, "zone": "Library Zone", "status": "STANDING", "entered_at": "20:00:01"},
    {"id": 22, "zone": "Canteen",      "status": "MOVING",   "entered_at": "19:48:09"},
    {"id": 24, "zone": "Main Gate",    "status": "MOVING",   "entered_at": "20:02:44"},
    {"id": 25, "zone": "ATM Zone 2",   "status": "STANDING", "entered_at": "19:59:17"},
]

# ─── Zone status ──────────────────────────────────────────────────────────────
ZONE_STATUS_BASE = [
    {"zone": "ATM Zone 1",       "level": "CRITICAL", "note": "UPI Fraud + Loitering",        "emoji": "🔴"},
    {"zone": "Entry Gate Cam 1", "level": "CRITICAL", "note": "Weapon detected 15 min ago",   "emoji": "🔴"},
    {"zone": "Hostel Corridor B","level": "HIGH",     "note": "Fall alert resolved",           "emoji": "🟡"},
    {"zone": "ATM Zone 2",       "level": "HIGH",     "note": "Loitering pattern",             "emoji": "🟡"},
    {"zone": "ENTRY_LOBBY",      "level": "LOW",      "note": "Normal activity",               "emoji": "🟢"},
    {"zone": "Library Zone",     "level": "CLEAR",    "note": "No alerts",                     "emoji": "🟢"},
    {"zone": "Canteen",          "level": "CLEAR",    "note": "No alerts",                     "emoji": "🟢"},
]


def get_zone_status_live() -> list[dict]:
    """Return zone status with slight randomization on low-risk zones."""
    zones = []
    for z in ZONE_STATUS_BASE:
        entry = z.copy()
        if z["level"] in ("CLEAR", "LOW"):
            entry["level"] = random.choice(["CLEAR", "MONITOR"])
            if entry["level"] == "MONITOR":
                entry["emoji"] = "🟡"
                entry["note"] = "Routine patrol scheduled"
        zones.append(entry)
    return zones


# ─── Health metrics (incrementing fake uptime) ────────────────────────────────
_BASE_UPTIME_SECONDS = 9251   # ~2h 34m 11s at first call

def get_fake_health() -> dict:
    """Return fake health metrics with small random increments each call."""
    extra = random.randint(0, 300)
    total = _BASE_UPTIME_SECONDS + extra
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return {
        "uptime": f"{h:02d}h {m:02d}m {s:02d}s",
        "alerts_today": 12 + random.randint(0, 3),
        "resolved": 9 + random.randint(0, 2),
        "escalated": 3 + random.randint(0, 1),
    }
