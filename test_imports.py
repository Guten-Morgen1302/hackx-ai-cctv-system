#!/usr/bin/env python
"""Quick import test"""
try:
    from survilleance.Detector import Detector_2A2S
    print("OK: Detector imported")
except Exception as e:
    print(f"FAIL Detector: {e}")

try:
    from modules.voice_call_handler import schedule_voice_call_in_15_seconds
    print("OK: Voice handler imported")
except Exception as e:
    print(f"FAIL Voice handler: {e}")

try:
    from modules.twilio_webhook import twilio_bp
    print("OK: Twilio webhook imported")
except Exception as e:
    print(f"FAIL Twilio webhook: {e}")

print("\nAll imports successful!")
