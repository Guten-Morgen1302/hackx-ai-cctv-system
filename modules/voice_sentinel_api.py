"""
Voice Sentinel Flask Blueprint
Provides REST API endpoints for generating automated security alert calls.
"""

from flask import Blueprint, request, jsonify
from modules.voice_sentinel import create_alert_call_script
from typing import Dict, Any

voice_sentinel_bp = Blueprint("voice_sentinel", __name__, url_prefix="/api/voice")


@voice_sentinel_bp.route("/alert", methods=["POST"])
def generate_alert():
    """
    Generate a voice alert call script from a security event.

    Expects JSON body with security event data:
    {
        "event_type": "FALL_DETECTED",
        "risk_tier": "CRITICAL",
        "zone_name": "Location",
        "short_reason": "Description",
        "time_ago_seconds": 18,
        "extra_details": "Additional info",
        "recommended_actions": ["action1", "action2"]
    }

    Returns:
    {
        "spoken_message": "The voice message to play",
        "dtmf_menu": "The DTMF keypad instructions",
        "full_script": "Complete script for logging",
        "timestamp": "ISO timestamp"
    }
    """
    try:
        event_data = request.get_json()

        if not event_data:
            return jsonify({"error": "No JSON body provided"}), 400

        # Validate required fields
        if "event_type" not in event_data or "risk_tier" not in event_data:
            return (
                jsonify(
                    {
                        "error": "Missing required fields: event_type, risk_tier",
                    }
                ),
                400,
            )

        # Generate alert script
        result = create_alert_call_script(event_data)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


@voice_sentinel_bp.route("/alert/test", methods=["GET"])
def test_alert():
    """
    Test endpoint with pre-defined fall detection event.
    Useful for testing integration without external event sources.
    """
    test_event = {
        "event_type": "FALL_DETECTED",
        "risk_tier": "CRITICAL",
        "zone_name": "Hostel Corridor, Building A",
        "short_reason": "Person has been on the floor for 12 seconds without moving",
        "time_ago_seconds": 18,
        "extra_details": "Camera 3, Night Mode",
        "recommended_actions": [
            "Send a staff member to check the area immediately",
        ],
    }

    result = create_alert_call_script(test_event)
    return jsonify(result), 200


@voice_sentinel_bp.route("/alert/preview", methods=["POST"])
def preview_alert():
    """
    Preview endpoint that returns formatted text suitable for display.
    Does NOT trigger actual voice call, just shows what would be said.
    """
    try:
        event_data = request.get_json()

        if not event_data:
            return jsonify({"error": "No JSON body provided"}), 400

        result = create_alert_call_script(event_data)

        return (
            jsonify(
                {
                    "event_type": event_data.get("event_type"),
                    "zone_name": event_data.get("zone_name"),
                    "risk_tier": event_data.get("risk_tier"),
                    "preview": {
                        "spoken_message": result["spoken_message"],
                        "dtmf_menu": result["dtmf_menu"],
                        "estimated_duration_seconds": len(
                            result["spoken_message"].split()
                        )
                        * 0.5,  # Rough estimate
                    },
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@voice_sentinel_bp.route("/events/templates", methods=["GET"])
def get_event_templates():
    """
    Returns example event templates for each event type.
    Useful for documentation and testing.
    """
    templates = {
        "FALL_DETECTED": {
            "event_type": "FALL_DETECTED",
            "risk_tier": "CRITICAL",
            "zone_name": "Hostel Corridor",
            "short_reason": "Person on floor without movement for 12 seconds",
            "time_ago_seconds": 10,
            "extra_details": "Camera 3, Night Mode",
            "recommended_actions": [
                "Send a staff member to check immediately",
            ],
        },
        "ABANDONED_OBJECT": {
            "event_type": "ABANDONED_OBJECT",
            "risk_tier": "HIGH",
            "zone_name": "ATM Zone 1",
            "short_reason": "Unattended bag detected for 2+ minutes",
            "recommended_actions": ["Send guard to inspect object"],
        },
        "SHADOW_DETECTED": {
            "event_type": "SHADOW_DETECTED",
            "risk_tier": "MEDIUM",
            "zone_name": "Campus Perimeter, Night Zone",
            "short_reason": "Movement in low-light area detected",
            "extra_details": "Camera 5, 23:45 hours",
            "recommended_actions": ["Check camera zone for intruder"],
        },
        "LOITERING": {
            "event_type": "LOITERING",
            "risk_tier": "MEDIUM",
            "zone_name": "Restricted Area, Lab Wing",
            "short_reason": "Person loitering for 5+ minutes in restricted zone",
            "recommended_actions": [
                "Ask person to leave the restricted area",
            ],
        },
        "WEAPON": {
            "event_type": "WEAPON",
            "risk_tier": "CRITICAL",
            "zone_name": "Main Campus Entrance",
            "short_reason": "Possible weapon detected in carry bag",
            "recommended_actions": ["Activate emergency protocol immediately"],
        },
        "UPI_FRAUD": {
            "event_type": "UPI_FRAUD",
            "risk_tier": "HIGH",
            "zone_name": "ATM Zone 2",
            "short_reason": "High-risk UPI transaction detected",
            "recommended_actions": ["Review transaction and contact user"],
        },
        "CROSS_DOMAIN": {
            "event_type": "CROSS_DOMAIN",
            "risk_tier": "CRITICAL",
            "zone_name": "ATM Zone 1",
            "short_reason": "Suspicious person + high-risk UPI transaction detected simultaneously",
            "recommended_actions": [
                "Follow emergency security procedure",
            ],
        },
    }

    return jsonify(templates), 200
