"""
SecureVista Voice Sentinel — Integration Examples
Demonstrates how to use Voice Sentinel in production scenarios
"""

# ============================================================================
# EXAMPLE 1: Direct Python Module Usage
# ============================================================================

def example_direct_module():
    """Use Voice Sentinel directly in Python code"""
    from modules.voice_sentinel import create_alert_call_script

    # Create a security event
    event = {
        "event_type": "FALL_DETECTED",
        "risk_tier": "CRITICAL",
        "zone_name": "Hostel Corridor, Building A",
        "short_reason": "Person on floor without movement for 12 seconds",
        "time_ago_seconds": 18,
        "extra_details": "Camera 3, Night Mode",
        "recommended_actions": [
            "Send a staff member to check the area immediately",
            "Ensure the person is safe and provide assistance",
        ],
    }

    # Generate alert
    result = create_alert_call_script(event)

    # Use the results
    print("SPOKEN MESSAGE:")
    print(result["spoken_message"])
    print("\nDTMF MENU:")
    print(result["dtmf_menu"])
    print("\nFULL SCRIPT:")
    print(result["full_script"])
    print(f"\nTimestamp: {result['timestamp']}")


# ============================================================================
# EXAMPLE 2: REST API Usage (curl / requests)
# ============================================================================

def example_rest_api():
    """Call Voice Sentinel via REST API"""
    import requests
    import json

    # Event data
    event_data = {
        "event_type": "ABANDONED_OBJECT",
        "risk_tier": "HIGH",
        "zone_name": "ATM Zone 1, Andheri Branch",
        "short_reason": "Unattended bag detected for 2+ minutes",
        "recommended_actions": ["Send a guard to inspect the object"],
    }

    # Make API call
    response = requests.post(
        "http://localhost:7860/api/voice/alert", json=event_data
    )

    if response.status_code == 200:
        alert = response.json()
        print("✓ Alert generated successfully")
        print(f"Spoken: {alert['spoken_message'][:50]}...")
        print(f"DTMF: {alert['dtmf_menu'][:50]}...")
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.json())


# ============================================================================
# EXAMPLE 3: Twilio Integration
# ============================================================================

def example_twilio_integration():
    """Integrate Voice Sentinel with Twilio for actual phone calls"""
    import requests
    from twilio.rest import Client

    # Configuration (replace with real values)
    TWILIO_ACCOUNT_SID = "your_account_sid"
    TWILIO_AUTH_TOKEN = "your_auth_token"
    TWILIO_NUMBER = "+1234567890"  # Twilio phone number
    SECURITY_PHONE = "+919876543210"  # Security guard's phone

    # Step 1: Get alert from Voice Sentinel
    event = {
        "event_type": "FALL_DETECTED",
        "risk_tier": "CRITICAL",
        "zone_name": "Hostel Corridor",
        "short_reason": "Person on floor without movement",
    }

    response = requests.post("http://localhost:7860/api/voice/alert", json=event)
    alert = response.json()

    # Step 2: Create Twilio TwiML
    twiml = f"""
    <Response>
        <Say voice="alice">{alert['spoken_message']}</Say>
        <Gather numDigits="1" timeout="10" action="/handle-dtmf" method="POST">
            <Say>{alert['dtmf_menu']}</Say>
        </Gather>
        <Say>Thank you for confirming. Goodbye.</Say>
    </Response>
    """

    # Step 3: Make the call
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    call = client.calls.create(
        to=SECURITY_PHONE, from_=TWILIO_NUMBER, twiml=twiml
    )

    print(f"✓ Call initiated: {call.sid}")
    return call.sid


# ============================================================================
# EXAMPLE 4: Vapi Integration (Advanced Voice Agent)
# ============================================================================

def example_vapi_integration():
    """Integrate with Vapi for advanced voice agent capabilities"""
    import requests

    VAPI_API_KEY = "your_vapi_api_key"
    VAPI_API_URL = "https://api.vapi.ai/call"

    # Get alert from Voice Sentinel
    event = {
        "event_type": "SHADOW_DETECTED",
        "risk_tier": "MEDIUM",
        "zone_name": "Campus Perimeter",
        "short_reason": "Movement in low-light area detected",
    }

    sentinel_response = requests.post(
        "http://localhost:7860/api/voice/alert", json=event
    )
    alert = sentinel_response.json()

    # Vapi call configuration
    vapi_payload = {
        "phoneNumber": "+919876543210",
        "systemPrompt": alert["spoken_message"],
        "firstMessage": alert["dtmf_menu"],
        "endCallMessage": "Thank you. Goodbye.",
        "voiceId": "google-neural-2",  # High-quality voice
    }

    # Make Vapi call
    headers = {"Authorization": f"Bearer {VAPI_API_KEY}"}
    response = requests.post(VAPI_API_URL, json=vapi_payload, headers=headers)

    if response.status_code == 201:
        print("✓ Vapi call created successfully")
        print(f"Call ID: {response.json()['id']}")
    else:
        print(f"✗ Error: {response.status_code}")


# ============================================================================
# EXAMPLE 5: Integration with Enhanced Detector
# ============================================================================

def example_with_enhanced_detector():
    """Integrate Voice Sentinel with the Enhanced2A2SDetector"""
    import requests
    from modules.enhanced_detector import Enhanced2A2SDetector

    # Simulate detection results from Enhanced2A2SDetector
    detection_results = {
        "fall_detected": True,
        "fall_confidence": 0.94,
        "fall_person_id": "person_123",
        "fall_zone": "Hostel Corridor, Building A",
        "fall_duration_seconds": 12,
    }

    # Convert detection results to Voice Sentinel event
    if detection_results["fall_detected"]:
        event = {
            "event_type": "FALL_DETECTED",
            "risk_tier": "CRITICAL",
            "zone_name": detection_results["fall_zone"],
            "short_reason": f"Person has been on the floor for {detection_results['fall_duration_seconds']} seconds without moving",
            "confidence": detection_results["fall_confidence"],
            "recommended_actions": [
                "Send a staff member to check the area immediately"
            ],
        }

        # Generate and send alert
        response = requests.post(
            "http://localhost:7860/api/voice/alert", json=event
        )
        alert = response.json()
        print(f"Alert generated: {alert['timestamp']}")
        print(alert["spoken_message"])


# ============================================================================
# EXAMPLE 6: Batch Processing Multiple Events
# ============================================================================

def example_batch_processing():
    """Process multiple security events in sequence"""
    import requests
    import time

    events = [
        {
            "event_type": "SHADOW_DETECTED",
            "risk_tier": "MEDIUM",
            "zone_name": "Campus Perimeter",
            "short_reason": "Unauthorized movement detected",
        },
        {
            "event_type": "ABANDONED_OBJECT",
            "risk_tier": "HIGH",
            "zone_name": "ATM Zone 1",
            "short_reason": "Unattended package detected",
        },
        {
            "event_type": "LOITERING",
            "risk_tier": "MEDIUM",
            "zone_name": "Restricted Area",
            "short_reason": "Person lingering in restricted zone",
        },
    ]

    alerts_generated = []

    for event in events:
        print(f"\nProcessing: {event['event_type']} at {event['zone_name']}")

        response = requests.post(
            "http://localhost:7860/api/voice/alert", json=event
        )

        if response.status_code == 200:
            alert = response.json()
            alerts_generated.append(alert)
            print(f"✓ Alert generated ({len(alerts_generated)}/{len(events)})")
            time.sleep(1)  # Brief delay between calls
        else:
            print(f"✗ Failed: {response.status_code}")

    print(f"\n✓ Batch processing complete: {len(alerts_generated)} alerts generated")
    return alerts_generated


# ============================================================================
# EXAMPLE 7: Preview Alert Before Calling
# ============================================================================

def example_preview_alert():
    """Preview an alert without actually making a call"""
    import requests

    event = {
        "event_type": "WEAPON",
        "risk_tier": "CRITICAL",
        "zone_name": "Main Campus Entrance",
        "short_reason": "Possible weapon detected in bag",
    }

    # Use preview endpoint
    response = requests.post(
        "http://localhost:7860/api/voice/alert/preview", json=event
    )

    preview = response.json()
    print("PREVIEW (No call made):")
    print(f"Event: {preview['event_type']} - {preview['risk_tier']}")
    print(f"Location: {preview['zone_name']}")
    print(f"Estimated Duration: {preview['preview']['estimated_duration_seconds']:.1f}s")
    print("\nSpoken Message:")
    print(preview["preview"]["spoken_message"])
    print("\nDTMF Menu:")
    print(preview["preview"]["dtmf_menu"])


# ============================================================================
# EXAMPLE 8: Get Event Templates
# ============================================================================

def example_get_templates():
    """Retrieve template examples for all event types"""
    import requests
    import json

    response = requests.get("http://localhost:7860/api/voice/events/templates")
    templates = response.json()

    print("Available Event Templates:")
    print("=" * 50)

    for event_type, template in templates.items():
        print(f"\n{event_type}:")
        print(f"  Risk Tier: {template['risk_tier']}")
        print(f"  Zone: {template['zone_name']}")
        print(f"  Reason: {template['short_reason']}")


# ============================================================================
# EXAMPLE 9: Custom TTS Voice Configuration
# ============================================================================

def example_custom_tts():
    """Use custom TTS voices (requires TTS service setup)"""
    import requests
    import subprocess
    import os

    # Step 1: Get alert from Voice Sentinel
    event = {
        "event_type": "FALL_DETECTED",
        "risk_tier": "CRITICAL",
        "zone_name": "Hostel Corridor",
        "short_reason": "Person on floor without movement",
    }

    response = requests.post("http://localhost:7860/api/voice/alert", json=event)
    alert = response.json()

    # Step 2: Convert text to speech using Google Cloud TTS
    # (Requires Google Cloud credentials)
    text_to_synthesize = alert["spoken_message"]

    # Alternative: Use gTTS (free, offline)
    try:
        from gtts import gTTS

        tts = gTTS(text_to_synthesize, lang="en", slow=False)
        tts.save("alert_message.mp3")
        print("✓ Alert audio saved to: alert_message.mp3")

        # Play the audio (optional)
        if os.name == "nt":  # Windows
            os.system("start alert_message.mp3")
    except ImportError:
        print("Install gTTS: pip install gtts")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("SecureVista Voice Sentinel — Integration Examples")
    print("=" * 70)

    # Run examples (uncomment to test)
    print("\n[EXAMPLE 1] Direct Module Usage")
    print("-" * 70)
    example_direct_module()

    print("\n[EXAMPLE 2] REST API Usage")
    print("-" * 70)
    # example_rest_api()  # Requires running app.py

    print("\n[EXAMPLE 7] Preview Alert")
    print("-" * 70)
    # example_preview_alert()  # Requires running app.py

    print("\n[EXAMPLE 8] Get Templates")
    print("-" * 70)
    # example_get_templates()  # Requires running app.py

    print("\n" + "=" * 70)
    print("Examples completed. See function definitions for more scenarios.")
    print("=" * 70)
