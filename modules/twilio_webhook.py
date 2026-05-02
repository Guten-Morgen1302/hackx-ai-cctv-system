"""
SecureVista Twilio DTMF Webhook Blueprint
Handles DTMF responses from Twilio calls and incident tracking.
"""

from flask import Blueprint, request, Response
import logging
from modules.voice_call_handler import handle_dtmf_response

logger = logging.getLogger(__name__)

twilio_bp = Blueprint("twilio", __name__, url_prefix="/twilio")


@twilio_bp.route("/dtmf", methods=["POST"])
def handle_dtmf():
    """
    Webhook endpoint for Twilio DTMF responses.
    
    Query parameters:
        incident_id: ID of the incident
        
    Form data (from Twilio):
        Digits: Pressed digit (1 or 2)
        CallSid: Twilio call ID
    """
    try:
        # Get parameters
        incident_id = request.args.get("incident_id", "UNKNOWN")
        digits = request.form.get("Digits", "")
        call_sid = request.form.get("CallSid", "")

        logger.info(
            f"DTMF received - Incident: {incident_id}, Digit: {digits}, CallSid: {call_sid}"
        )

        # Handle the response
        # Pass save_response_fn if you want to store DTMF responses in DB
        twiml = handle_dtmf_response(
            digit=digits,
            call_sid=call_sid,
            incident_id=incident_id,
            save_response_fn=None,  # Replace with your DB callback if desired
        )

        # Return TwiML response
        return Response(twiml, mimetype="text/xml")

    except Exception as e:
        logger.error(f"Error handling DTMF: {str(e)}")
        # Return safe TwiML error response
        from twilio.twiml.voice_response import VoiceResponse

        response = VoiceResponse()
        response.say("An error occurred. Please try again later.")
        response.hangup()
        return Response(str(response), mimetype="text/xml")


@twilio_bp.route("/status", methods=["POST"])
def handle_call_status():
    """
    Optional: Webhook for Twilio call status updates.
    Called when call completes.
    
    Form data (from Twilio):
        CallSid: Twilio call ID
        CallStatus: Status (completed, busy, failed, no-answer, etc.)
    """
    try:
        call_sid = request.form.get("CallSid", "")
        call_status = request.form.get("CallStatus", "")
        incident_id = request.args.get("incident_id", "UNKNOWN")

        logger.info(
            f"Call status update - CallSid: {call_sid}, Status: {call_status}, Incident: {incident_id}"
        )

        # You can store this information in your database if needed
        # Example: save_call_status(incident_id, call_sid, call_status)

        return Response("", status=200)

    except Exception as e:
        logger.error(f"Error handling call status: {str(e)}")
        return Response("", status=500)


@twilio_bp.route("/test", methods=["GET"])
def test_webhook():
    """
    Simple test endpoint to verify webhook is running.
    """
    return {
        "status": "ok",
        "message": "Twilio webhook is running",
        "endpoints": {
            "dtmf": "/twilio/dtmf",
            "status": "/twilio/status",
        },
    }
