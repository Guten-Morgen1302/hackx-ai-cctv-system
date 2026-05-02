# SecureVista Voice Sentinel — Complete Documentation

## Overview

**Voice Sentinel** is an automated security officer system that generates professional, calm voice alerts for security incidents detected by SecureVista. It processes security events in real-time and produces:

1. **Spoken Message** — A brief, professional voice message explaining the incident
2. **DTMF Menu** — A keypad menu for the recipient to acknowledge or escalate

## Key Features

✅ **Professional Tone** — Calm, serious, like a trained security control-room operator  
✅ **Sub-60-Second Alerts** — All messages fit within recommended call duration  
✅ **Event-Specific Messaging** — Tailored responses for 7+ event types  
✅ **Risk-Based DTMF** — Keypad menus vary by criticality level  
✅ **Zero Small Talk** — Direct, no-nonsense communication  
✅ **Simple English** — Short sentences, accessible language  

---

## Supported Event Types

| Event Type | Risk Level | Typical Duration |
|---|---|---|
| **FALL_DETECTED** | CRITICAL | ~30 seconds |
| **ABANDONED_OBJECT** | HIGH | ~25 seconds |
| **SHADOW_DETECTED** | MEDIUM | ~20 seconds |
| **LOITERING** | MEDIUM | ~20 seconds |
| **WEAPON** | CRITICAL | ~35 seconds |
| **UPI_FRAUD** | HIGH | ~25 seconds |
| **CROSS_DOMAIN** | CRITICAL | ~40 seconds |

---

## Event JSON Input Format

Voice Sentinel expects one JSON object with the following structure:

```json
{
  "event_type": "FALL_DETECTED | ABANDONED_OBJECT | SHADOW_DETECTED | LOITERING | WEAPON | UPI_FRAUD | CROSS_DOMAIN",
  "risk_tier": "CRITICAL | HIGH | MEDIUM",
  "zone_name": "ATM Zone 1, Andheri Branch",
  "short_reason": "Person has been on the floor for 12 seconds without moving",
  "time_ago_seconds": 18,
  "extra_details": "Camera 3, Hostel Corridor, Night Mode",
  "recommended_actions": [
    "Send a staff member to check the area immediately",
    "Do not ignore this alert until someone has visually confirmed the situation"
  ]
}
```

### Field Descriptions

| Field | Required | Description |
|---|---|---|
| `event_type` | ✅ Yes | Type of security event detected |
| `risk_tier` | ✅ Yes | Severity: CRITICAL, HIGH, or MEDIUM |
| `zone_name` | ✅ Yes | Location where event occurred (e.g., "ATM Zone 1, Andheri Branch") |
| `short_reason` | ✅ Yes | Brief, human-readable explanation of the event |
| `time_ago_seconds` | ❌ No | Seconds elapsed since event detection (informational only) |
| `extra_details` | ❌ No | Additional context (camera name, time, mode, etc.) |
| `recommended_actions` | ❌ No | List of suggested immediate actions; first item is used in alert |

**Note:** Missing optional fields are safely ignored; the system will still generate a valid alert message.

---

## Output Format

Voice Sentinel returns a JSON object with two main blocks:

```json
{
  "spoken_message": "Hello, this is the SecureVista automated security system calling.\nA possible fall has been detected in Hostel Corridor...",
  "dtmf_menu": "If everything is safe and this alert is expected, press 1. If you need help...",
  "full_script": "Combined script for voice playback and logging",
  "timestamp": "2026-05-02T14:35:22.123456"
}
```

---

## API Endpoints

### 1. Generate Alert (POST `/api/voice/alert`)

Generate a voice alert call script from a security event.

**Request:**
```bash
curl -X POST http://localhost:7860/api/voice/alert \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "FALL_DETECTED",
    "risk_tier": "CRITICAL",
    "zone_name": "Hostel Corridor",
    "short_reason": "Person on floor without movement",
    "recommended_actions": ["Send staff member immediately"]
  }'
```

**Response:**
```json
{
  "spoken_message": "Hello, this is the SecureVista...",
  "dtmf_menu": "If everything is safe...",
  "full_script": "...",
  "timestamp": "2026-05-02T14:35:22.123456"
}
```

---

### 2. Test Alert (GET `/api/voice/alert/test`)

Test endpoint with a pre-configured fall detection event. Useful for testing integration without external event data.

**Request:**
```bash
curl http://localhost:7860/api/voice/alert/test
```

**Response:** Same format as POST `/api/voice/alert`

---

### 3. Preview Alert (POST `/api/voice/alert/preview`)

Preview an alert message without triggering a call. Returns formatted display text.

**Request:**
```bash
curl -X POST http://localhost:7860/api/voice/alert/preview \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "ABANDONED_OBJECT",
    "risk_tier": "HIGH",
    "zone_name": "ATM Zone 1"
  }'
```

**Response:**
```json
{
  "event_type": "ABANDONED_OBJECT",
  "zone_name": "ATM Zone 1",
  "risk_tier": "HIGH",
  "preview": {
    "spoken_message": "...",
    "dtmf_menu": "...",
    "estimated_duration_seconds": 25.5
  }
}
```

---

### 4. Event Templates (GET `/api/voice/events/templates`)

Returns example JSON templates for all supported event types.

**Request:**
```bash
curl http://localhost:7860/api/voice/events/templates
```

**Response:**
```json
{
  "FALL_DETECTED": { ... },
  "ABANDONED_OBJECT": { ... },
  "SHADOW_DETECTED": { ... },
  "LOITERING": { ... },
  "WEAPON": { ... },
  "UPI_FRAUD": { ... },
  "CROSS_DOMAIN": { ... }
}
```

---

## Example Conversations

### Example 1: Fall Detected (CRITICAL)

**Input:**
```json
{
  "event_type": "FALL_DETECTED",
  "risk_tier": "CRITICAL",
  "zone_name": "Hostel Corridor, Building A",
  "short_reason": "Person has been on the floor for 12 seconds without moving",
  "recommended_actions": ["Send a staff member to check the area immediately"]
}
```

**Output:**
```
[SPOKEN_MESSAGE]
Hello, this is the SecureVista automated security system calling.
A possible fall has been detected in Hostel Corridor, Building A, where Person has been on the floor for 12 seconds without moving. Send a staff member to check the area immediately
We have already logged this as a critical incident in your SecureVista dashboard.

[DTMF_MENU]
If everything is safe and this alert is expected, press 1. If you need help or want to escalate this incident, press 2.
```

---

### Example 2: Abandoned Object (HIGH)

**Input:**
```json
{
  "event_type": "ABANDONED_OBJECT",
  "risk_tier": "HIGH",
  "zone_name": "ATM Zone 1, Andheri Branch",
  "short_reason": "Unattended bag left for more than two minutes",
  "recommended_actions": ["Send a guard to inspect the object immediately"]
}
```

**Output:**
```
[SPOKEN_MESSAGE]
Hello, this is the SecureVista automated security system calling.
An unattended object has been detected in ATM Zone 1, Andheri Branch. Unattended bag left for more than two minutes. Send a guard to inspect the object immediately

[DTMF_MENU]
If everything is safe and this alert is expected, press 1. If you need help or want to escalate this incident, press 2.
```

---

### Example 3: Cross-Domain Fraud (CRITICAL)

**Input:**
```json
{
  "event_type": "CROSS_DOMAIN",
  "risk_tier": "CRITICAL",
  "zone_name": "ATM Zone 1",
  "short_reason": "Suspicious person near ATM detected simultaneously with high-risk UPI transaction"
}
```

**Output:**
```
[SPOKEN_MESSAGE]
Hello, this is the SecureVista automated security system calling.
A critical cross-domain security event has been detected at ATM Zone 1. Suspicious person near ATM detected simultaneously with high-risk UPI transaction.
We have already logged this as a critical incident in your SecureVista dashboard.

[DTMF_MENU]
If everything is safe and this alert is expected, press 1. If you need help or want to escalate this incident, press 2.
```

---

## DTMF Menu Behavior

### CRITICAL & HIGH Risk Events
Recipients receive a keypad menu:
- **Press 1** — Acknowledge alert, confirm everything is safe
- **Press 2** — Request escalation, need help with incident

### MEDIUM Risk Events
No keypad input required (informational alert only).

---

## Integration with Voice Platforms

### Twilio Integration

```python
from twilio.rest import Client
from modules.voice_sentinel import create_alert_call_script

client = Client(TWILIO_SID, TWILIO_TOKEN)

event = {
    "event_type": "FALL_DETECTED",
    "risk_tier": "CRITICAL",
    "zone_name": "Building A"
}

alert = create_alert_call_script(event)

call = client.calls.create(
    to=SECURITY_PHONE,
    from_=TWILIO_NUMBER,
    twiml=f'<Response><Say>{alert["spoken_message"]}</Say><Gather numDigits="1"><Say>{alert["dtmf_menu"]}</Say></Gather></Response>'
)
```

### Vapi Integration

```python
# Use the /api/voice/alert endpoint to get the spoken_message
# Feed it to Vapi's TTS and <Gather> for DTMF collection
response = requests.post(
    'http://localhost:7860/api/voice/alert',
    json=event_data
)
```

---

## Python Module Usage

### Direct Import

```python
from modules.voice_sentinel import VoiceSentinel, create_alert_call_script

# Method 1: High-level function
event = {
    "event_type": "FALL_DETECTED",
    "risk_tier": "CRITICAL",
    "zone_name": "Hostel"
}
result = create_alert_call_script(event)
print(result["spoken_message"])
print(result["dtmf_menu"])

# Method 2: Using VoiceSentinel class directly
sentinel = VoiceSentinel()
spoken, dtmf = sentinel.process_event(event)
print(f"Voice: {spoken}")
print(f"Menu: {dtmf}")
```

---

## Testing

### Run Module Tests

```bash
python modules/voice_sentinel.py
```

This will execute three test scenarios:
1. Fall detection (CRITICAL)
2. Abandoned object (HIGH)
3. Cross-domain fraud (CRITICAL)

### Test via API

```bash
# Test with GET
curl http://localhost:7860/api/voice/alert/test

# Test with custom event
curl -X POST http://localhost:7860/api/voice/alert \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "SHADOW_DETECTED",
    "risk_tier": "MEDIUM",
    "zone_name": "Campus Perimeter"
  }'
```

---

## Design Principles

### 1. **Professional Tone**
- Never mention AI, models, or technical details
- Always call yourself "the SecureVista automated security system"
- Calm, reassuring, but serious

### 2. **Speed**
- All messages under 60 seconds
- No filler words or explanations
- Direct, actionable information only

### 3. **Clarity**
- Simple English, short sentences
- No jargon or acronyms (except event types)
- Neutral Indian accent compatible

### 4. **Consistency**
- Same introduction every call
- Standardized event message format
- Predictable DTMF menu

### 5. **Safety**
- CRITICAL alerts include dashboard confirmation
- HIGH/CRITICAL events always include keypad menu
- Recommended actions are extracted from event data

---

## Error Handling

### Missing Required Fields
```json
{
  "error": "Missing required fields: event_type, risk_tier"
}
```

### Invalid JSON
```json
{
  "error": "No JSON body provided"
}
```

### Server Error
```json
{
  "error": "Internal error: [error details]"
}
```

---

## Deployment

### Docker
Voice Sentinel API is automatically included in the SecureVista Docker image on port 7860.

### Production Setup
1. Voice Sentinel is registered in `app.py` at Flask startup
2. Blueprints are available at `/api/voice/*` endpoints
3. Compatible with Twilio, Vapi, or custom voice platforms

---

## Roadmap

- [ ] Custom TTS voice profiles (male/female)
- [ ] Multilingual support (Hindi, Marathi, etc.)
- [ ] Callback logging to SecurityLog DB
- [ ] DTMF response storage for compliance
- [ ] Integration with alert suppression rules
- [ ] Voice message templates customization

---

## Support

For issues or feature requests, refer to:
- `modules/voice_sentinel.py` — Core logic
- `modules/voice_sentinel_api.py` — Flask integration
- `tests/` — Test cases

---

**SecureVista Voice Sentinel v1.0** — Deployed May 2, 2026
