"""
SecureVista Voice Sentinel
Automated security officer for voice alert calls.
Processes security events and generates voice-based alerts with DTMF menu.
"""

from typing import Dict, Any, Tuple
from datetime import datetime
import json


class VoiceSentinel:
    """
    Generates voice alerts for security events.
    Outputs structured voice messages and DTMF menus.
    """

    def __init__(self):
        self.system_name = "SecureVista automated security system"
        self.intro = "Hello, this is the SecureVista automated security system calling."

    def process_event(self, event: Dict[str, Any]) -> Tuple[str, str]:
        """
        Process security event and return spoken message + DTMF menu.

        Args:
            event: Dict with keys:
                - event_type: FALL_DETECTED, ABANDONED_OBJECT, SHADOW_DETECTED, LOITERING, WEAPON, UPI_FRAUD, CROSS_DOMAIN
                - risk_tier: CRITICAL, HIGH, MEDIUM
                - zone_name: Location string
                - short_reason: Brief description
                - time_ago_seconds: (optional) Seconds since event
                - extra_details: (optional) Additional context
                - recommended_actions: (optional) List of action strings

        Returns:
            Tuple of (spoken_message, dtmf_menu)
        """
        event_type = event.get("event_type", "UNKNOWN")
        risk_tier = event.get("risk_tier", "MEDIUM")
        zone_name = event.get("zone_name", "Unknown Location")
        short_reason = event.get("short_reason", "A security event has been detected")

        # Event-specific messages (no generic DTMF menu)
        if event_type == "FALL_DETECTED":
            spoken_message = f"Hello, this is the SecureVista security system. We detected a possible fall in {zone_name}. Please send someone to check that location now."
        elif event_type == "ABANDONED_OBJECT":
            spoken_message = f"Hello, this is the SecureVista security system. An unattended object was left in {zone_name}. Please ask a guard to inspect the area immediately."
        elif event_type == "SHADOW_DETECTED":
            spoken_message = f"Hello, this is the SecureVista security system. Our cameras detected suspicious shadow movement in {zone_name}. Please check the camera feed right away."
        else:
            spoken_message = f"Hello, this is the SecureVista security system. A security event has been detected in {zone_name}. Please take immediate action."

        # No DTMF menu - direct messages only
        dtmf_menu = ""

        return spoken_message, dtmf_menu

    def _generate_main_message(
        self,
        event_type: str,
        zone_name: str,
        short_reason: str,
        extra_details: str,
        recommended_actions: list,
    ) -> str:
        """Generate the main alert message based on event type."""

        action_text = (
            recommended_actions[0]
            if recommended_actions
            else "Please take immediate action."
        )

        if event_type == "FALL_DETECTED":
            return (
                f"A possible fall has been detected in {zone_name}, "
                f"where {short_reason}. {action_text}"
            )

        elif event_type == "ABANDONED_OBJECT":
            return (
                f"An unattended object has been detected in {zone_name}. {short_reason}. "
                f"{action_text}"
            )

        elif event_type == "SHADOW_DETECTED":
            return (
                f"Movement has been detected in a low-light area at {zone_name}. "
                f"{short_reason}. {action_text}"
            )

        elif event_type == "LOITERING":
            return (
                f"A person has been loitering in {zone_name}. {short_reason}. "
                f"{action_text}"
            )

        elif event_type == "WEAPON":
            return (
                f"A possible weapon has been detected in {zone_name}. {short_reason}. "
                f"{action_text}"
            )

        elif event_type == "UPI_FRAUD":
            return (
                f"A high-risk transaction has been detected at {zone_name}. "
                f"{short_reason}. {action_text}"
            )

        elif event_type == "CROSS_DOMAIN":
            return (
                f"A critical cross-domain security event has been detected at {zone_name}. "
                f"{short_reason}. {action_text}"
            )

        else:
            return (
                f"A security event has been detected in {zone_name}. {short_reason}. "
                f"{action_text}"
            )

    def _generate_dtmf_menu(self, risk_tier: str) -> str:
        """Generate DTMF keypad menu based on risk tier."""
        if risk_tier in ["CRITICAL", "HIGH"]:
            return "If everything is safe and this alert is expected, press 1. If you need help or want to escalate this incident, press 2."
        else:
            return "No keypad input is required for this alert."

    def format_for_voice(self, spoken_message: str, dtmf_menu: str) -> str:
        """
        Format the spoken message and DTMF menu for voice delivery.
        Returns plain text suitable for TTS.
        """
        return f"{spoken_message}\n\n{dtmf_menu}"

    def parse_json_event(self, json_string: str) -> Dict[str, Any]:
        """Parse JSON event string."""
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON event: {e}")


def create_alert_call_script(event_json: Dict[str, Any]) -> Dict[str, str]:
    """
    High-level function to create complete alert call script.

    Returns dict with:
        - spoken_message: The voice message to play
        - dtmf_menu: The keypad menu to offer
        - full_script: Combined script for logging/debugging
    """
    sentinel = VoiceSentinel()
    spoken_message, dtmf_menu = sentinel.process_event(event_json)

    return {
        "spoken_message": spoken_message.strip(),
        "dtmf_menu": dtmf_menu,
        "full_script": sentinel.format_for_voice(spoken_message, dtmf_menu).strip(),
        "timestamp": datetime.now().isoformat(),
    }


# Example usage for testing
if __name__ == "__main__":
    # Test event 1: Fall detected
    test_event_1 = {
        "event_type": "FALL_DETECTED",
        "risk_tier": "CRITICAL",
        "zone_name": "Hostel Corridor, Building A",
        "short_reason": "Person has been on the floor for 12 seconds without moving",
        "time_ago_seconds": 18,
        "extra_details": "Camera 3, Night Mode",
        "recommended_actions": [
            "Send a staff member to check the area immediately",
            "Do not ignore this alert until someone has visually confirmed the situation",
        ],
    }

    # Test event 2: Abandoned object
    test_event_2 = {
        "event_type": "ABANDONED_OBJECT",
        "risk_tier": "HIGH",
        "zone_name": "ATM Zone 1, Andheri Branch",
        "short_reason": "Unattended bag left for more than two minutes",
        "recommended_actions": [
            "Send a guard to inspect the object",
            "Follow your safety procedure if it looks suspicious",
        ],
    }

    # Test event 3: UPI Fraud
    test_event_3 = {
        "event_type": "CROSS_DOMAIN",
        "risk_tier": "CRITICAL",
        "zone_name": "ATM Zone 1",
        "short_reason": "Suspicious person near ATM detected simultaneously with high-risk UPI transaction",
        "recommended_actions": [
            "Follow your emergency security procedure immediately",
            "Review the alert in your SecureVista dashboard now",
        ],
    }

    print("=" * 70)
    print("TEST 1: FALL DETECTED (CRITICAL)")
    print("=" * 70)
    result_1 = create_alert_call_script(test_event_1)
    print(f"[SPOKEN_MESSAGE]\n{result_1['spoken_message']}\n")
    print(f"[DTMF_MENU]\n{result_1['dtmf_menu']}\n")

    print("=" * 70)
    print("TEST 2: ABANDONED OBJECT (HIGH)")
    print("=" * 70)
    result_2 = create_alert_call_script(test_event_2)
    print(f"[SPOKEN_MESSAGE]\n{result_2['spoken_message']}\n")
    print(f"[DTMF_MENU]\n{result_2['dtmf_menu']}\n")

    print("=" * 70)
    print("TEST 3: CROSS-DOMAIN FRAUD (CRITICAL)")
    print("=" * 70)
    result_3 = create_alert_call_script(test_event_3)
    print(f"[SPOKEN_MESSAGE]\n{result_3['spoken_message']}\n")
    print(f"[DTMF_MENU]\n{result_3['dtmf_menu']}\n")
