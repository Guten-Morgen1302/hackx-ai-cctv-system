"""
SecureVista Voice Call Handler
Integrates Voice Sentinel with Twilio for automated phone calls.
Handles DTMF responses and incident tracking.
"""

import os
import time
import threading
import json
import requests
import logging
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

logger = logging.getLogger(__name__)

# Environment variables
TWILIO_SID = os.getenv("TWILIO_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN", "")
TWILIO_FROM = os.getenv("TWILIO_FROM", "+15673502549")
GUARD_PHONE = os.getenv("GUARD_PHONE", "+91XXXXXXXXXX")
VOICE_SENTINEL_URL = os.getenv("VOICE_SENTINEL_URL", "http://localhost:5003/api/voice/alert")
WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL", "http://localhost:5003")

# Twilio client (initialized on first use)
_twilio_client = None

# Call cooldown tracking (prevent spam calls to same number)
_last_call_time = {}  # {phone_number: timestamp}
_pending_calls = set()  # phone numbers with a scheduled-but-not-yet-fired call
CALL_COOLDOWN_SECONDS = 60  # Don't call same number within 60 seconds


def get_twilio_client() -> Optional[Client]:
    """Get or initialize Twilio client."""
    global _twilio_client
    if not TWILIO_SID or not TWILIO_TOKEN:
        logger.warning("Twilio credentials not configured. Voice calls disabled.")
        return None
    if _twilio_client is None:
        _twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)
    return _twilio_client


def is_call_on_cooldown(phone_number: str) -> bool:
    """Check if phone number is on cooldown (prevent spam calls)."""
    global _last_call_time
    current_time = time.time()
    last_call = _last_call_time.get(phone_number)
    
    if last_call is None:
        return False
    
    time_since_last_call = current_time - last_call
    if time_since_last_call < CALL_COOLDOWN_SECONDS:
        logger.info(f"⏱️ Call cooldown active for {phone_number} ({CALL_COOLDOWN_SECONDS - time_since_last_call:.0f}s remaining)")
        return True
    
    return False


def is_call_pending(phone_number: str) -> bool:
    """Check if a call is already scheduled for this phone number."""
    return phone_number in _pending_calls


def record_call_time(phone_number: str) -> None:
    """Record when a call was made to a phone number."""
    global _last_call_time
    _last_call_time[phone_number] = time.time()


def should_trigger_voice_call(event: Dict[str, Any]) -> bool:
    """
    Determine if an event should trigger a voice call.
    
    Args:
        event: Security event dict with event_type and risk_tier
        
    Returns:
        True if voice call should be triggered, False otherwise
    """
    required_event_types = {
        "FALL_DETECTED",
        "ABANDONED_OBJECT",
        "SHADOW_DETECTED",
        "UPI_FRAUD",
        "CROSS_DOMAIN",
    }
    required_risk_tiers = {"CRITICAL", "HIGH"}

    event_type = event.get("event_type", "")
    risk_tier = event.get("risk_tier", "")

    return event_type in required_event_types and risk_tier in required_risk_tiers


def get_voice_alert(event: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """
    Fetch voice alert from Voice Sentinel API.
    
    Args:
        event: Security event dict
        
    Returns:
        Dict with 'spoken_message' and 'dtmf_menu' or None on error
    """
    try:
        response = requests.post(
            f"{VOICE_SENTINEL_URL}",
            json=event,
            timeout=5,
        )
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Voice Sentinel error: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Failed to get voice alert: {str(e)}")
        return None


def build_twilio_twiml(
    spoken_message: str,
    dtmf_menu: str,
    incident_id: str,
) -> str:
    """
    Build TwiML response for Twilio call.
    
    Args:
        spoken_message: Main alert message to speak
        dtmf_menu: DTMF menu instructions
        incident_id: Incident ID to pass to webhook
        
    Returns:
        TwiML XML string
    """
    response = VoiceResponse()

    # Play the spoken message
    response.say(spoken_message, voice="alice")

    # Only gather input when an explicit menu is provided
    if dtmf_menu:
        gather = response.gather(
            num_digits=1,
            action=f"{WEBHOOK_BASE_URL}/twilio/dtmf?incident_id={incident_id}",
            method="POST",
            timeout=10,
        )
        gather.say(dtmf_menu, voice="alice")

        # Fallback if no input
        response.say(
            "No input received. Your call has been logged. Thank you.",
            voice="alice",
        )

    return str(response)


def trigger_voice_call(event: Dict[str, Any], to_number: str) -> Optional[str]:
    """
    Trigger a Twilio voice call with Voice Sentinel message.
    
    Args:
        event: Security event dict (must include incident_id)
        to_number: Recipient phone number (e.g., +919876543210)
        
    Returns:
        Twilio call.sid on success, None on failure
    """
    client = get_twilio_client()
    if not client:
        logger.warning("Twilio client not available. Skipping voice call.")
        return None

    # Get voice alert from Voice Sentinel
    alert = get_voice_alert(event)
    if not alert:
        logger.error("Failed to get voice alert from Voice Sentinel")
        return None

    spoken_message = alert.get("spoken_message", "")
    dtmf_menu = alert.get("dtmf_menu", "")
    incident_id = event.get("incident_id", "UNKNOWN")

    if not spoken_message:
        logger.error("Empty spoken message from Voice Sentinel")
        return None

    try:
        # Build TwiML
        twiml = build_twilio_twiml(spoken_message, dtmf_menu, incident_id)

        # Make Twilio call
        call = client.calls.create(
            to=to_number,
            from_=TWILIO_FROM,
            twiml=twiml,
        )

        logger.info(
            f"Voice call initiated: {call.sid} for incident {incident_id} to {to_number}"
        )
        return call.sid

    except Exception as e:
        logger.error(f"Failed to make Twilio call: {str(e)}")
        return None


def schedule_voice_call_in_15_seconds(
    event: Dict[str, Any],
    to_number: str,
) -> None:
    """
    Schedule a voice call to be triggered after 15 seconds.
    Checks cooldown to prevent spam calls to same number.
    
    Args:
        event: Security event dict
        to_number: Recipient phone number
    """
    # Check if this number is already scheduled or on cooldown
    if is_call_pending(to_number):
        logger.info(f"Skipping voice call to {to_number} (already pending)")
        return
    if is_call_on_cooldown(to_number):
        logger.info(f"Skipping voice call to {to_number} (on cooldown)")
        return

    # Reserve immediately so repeated detections cannot queue another call
    _pending_calls.add(to_number)
    record_call_time(to_number)

    def _delayed():
        try:
            time.sleep(15)
            trigger_voice_call(event, to_number)
        finally:
            _pending_calls.discard(to_number)

    thread = threading.Thread(target=_delayed, daemon=True)
    thread.start()


def handle_dtmf_response(
    digit: str,
    call_sid: str,
    incident_id: str,
    save_response_fn=None,
) -> str:
    """
    Handle DTMF keypad response.
    
    Args:
        digit: Pressed digit ("1" or "2")
        call_sid: Twilio call SID
        incident_id: Incident ID
        save_response_fn: Optional callback to save response to DB
                         signature: save_response_fn(incident_id, digit, call_sid)
        
    Returns:
        TwiML response string
    """
    response_status = "UNKNOWN"

    if digit == "1":
        response_status = "ACKNOWLEDGED_SAFE"
        logger.info(f"Incident {incident_id}: Acknowledged safe (digit 1)")

    elif digit == "2":
        response_status = "ESCALATED"
        logger.info(f"Incident {incident_id}: Escalated (digit 2)")

    else:
        response_status = "INVALID_INPUT"
        logger.warning(f"Incident {incident_id}: Invalid DTMF digit {digit}")

    # Save response if callback provided
    if save_response_fn:
        try:
            save_response_fn(incident_id, digit, call_sid, response_status)
        except Exception as e:
            logger.error(f"Failed to save DTMF response: {str(e)}")

    # Build TwiML response
    twiml_response = VoiceResponse()
    twiml_response.say(
        "Thank you. Your response has been recorded. Goodbye.",
        voice="alice",
    )
    twiml_response.hangup()

    return str(twiml_response)


def test_fake_fall_call() -> None:
    """
    Test helper: Trigger a fake FALL_DETECTED voice call.
    Useful for testing the integration without real incidents.
    """
    event = {
        "incident_id": f"TEST-FALL-{int(time.time())}",
        "event_type": "FALL_DETECTED",
        "risk_tier": "HIGH",
        "zone_name": "Hostel Corridor, Camera 3",
        "short_reason": "Person on the floor without movement for 10 seconds",
        "recommended_actions": ["Send staff member immediately"],
    }

    logger.info("Test: Triggering fake fall call in 15 seconds...")
    schedule_voice_call_in_15_seconds(event, GUARD_PHONE)


def test_fake_weapon_call() -> None:
    """
    Test helper: Trigger a fake WEAPON voice call.
    """
    event = {
        "incident_id": f"TEST-WEAPON-{int(time.time())}",
        "event_type": "WEAPON",
        "risk_tier": "CRITICAL",
        "zone_name": "Main Campus Entrance",
        "short_reason": "Possible weapon detected in carry bag",
        "recommended_actions": ["Activate emergency protocol immediately"],
    }

    logger.info("Test: Triggering fake weapon call in 15 seconds...")
    schedule_voice_call_in_15_seconds(event, GUARD_PHONE)


# Example integration function (paste into your alert handler)
def handle_alert_with_voice(
    event: Dict[str, Any],
    save_to_db_fn=None,
    send_whatsapp_fn=None,
    push_to_dashboard_fn=None,
    save_dtmf_response_fn=None,
) -> None:
    """
    Handle security alert with existing functionality + voice calls.
    
    This function preserves existing behavior (DB, WhatsApp, dashboard)
    and adds voice calling as an additional step.
    
    Args:
        event: Security event dict
        save_to_db_fn: Callback to save incident to database
        send_whatsapp_fn: Callback to send WhatsApp alert
        push_to_dashboard_fn: Callback to push to dashboard
        save_dtmf_response_fn: Callback to save DTMF responses
    """
    # Existing behavior
    if save_to_db_fn:
        save_to_db_fn(event)

    if send_whatsapp_fn:
        send_whatsapp_fn(event)

    if push_to_dashboard_fn:
        push_to_dashboard_fn(event)

    # New behavior: Voice call
    if should_trigger_voice_call(event):
        guard_phone = GUARD_PHONE
        logger.info(f"Scheduling voice call for incident {event.get('incident_id')}")
        schedule_voice_call_in_15_seconds(event, guard_phone)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("SecureVista Voice Call Handler")
    print(f"Twilio From: {TWILIO_FROM}")
    print(f"Guard Phone: {GUARD_PHONE}")
    print(f"Voice Sentinel URL: {VOICE_SENTINEL_URL}")
    print("\nTest: Run test_fake_fall_call() to trigger a test call")
