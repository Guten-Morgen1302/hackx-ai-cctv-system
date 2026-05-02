#!/usr/bin/env python
"""
Voice Sentinel API Server (Standalone)
Runs on port 5003 to serve voice alert scripts to Twilio
"""

from flask import Flask, jsonify, request
from datetime import datetime
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Voice Sentinel Module
try:
    from modules.voice_sentinel import VoiceSentinel
    sentinel = VoiceSentinel()
    logger.info("✓ Voice Sentinel module loaded")
except ImportError as e:
    logger.warning(f"Voice Sentinel module not available: {e}")
    sentinel = None


@app.route('/api/voice/alert', methods=['GET', 'POST'])
def handle_voice_alert():
    """Generate voice alert script from event"""
    try:
        if request.method == 'GET':
            # Test endpoint with sample event
            event = {
                'event_type': 'FALL_DETECTED',
                'risk_tier': 'CRITICAL',
                'zone_name': 'Main Corridor',
                'short_reason': 'Person detected on ground',
                'incident_id': f'TEST-{int(datetime.now().timestamp())}',
            }
        else:
            event = request.get_json() or {}
        
        if not sentinel:
            return jsonify({
                'error': 'Voice Sentinel not available',
                'spoken_message': 'Voice system unavailable',
                'dtmf_menu': None,
                'full_script': None
            }), 503
        
        # Generate alert
        spoken_msg, dtmf_menu = sentinel.process_event(event)
        
        return jsonify({
            'incident_id': event.get('incident_id'),
            'event_type': event.get('event_type'),
            'spoken_message': spoken_msg,
            'dtmf_menu': dtmf_menu,
            'full_script': f"{spoken_msg}\n\n{dtmf_menu}" if dtmf_menu else spoken_msg,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in voice alert: {e}")
        return jsonify({
            'error': str(e),
            'spoken_message': 'An error occurred processing your security alert',
            'dtmf_menu': None
        }), 500


@app.route('/api/voice/alert/test', methods=['GET'])
def test_voice_alert():
    """Test endpoint"""
    return handle_voice_alert()


@app.route('/api/voice/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Voice Sentinel API',
        'timestamp': datetime.now().isoformat(),
        'voice_module_available': sentinel is not None
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'service': 'Voice Sentinel API Server',
        'version': '1.0',
        'endpoints': {
            'health': '/api/voice/health',
            'alert': '/api/voice/alert',
            'test': '/api/voice/alert/test'
        }
    }), 200


if __name__ == '__main__':
    port = 5003
    logger.info(f"🔊 Voice Sentinel API Server starting on http://localhost:{port}")
    logger.info(f"📍 Alert endpoint: http://localhost:{port}/api/voice/alert")
    logger.info(f"🧪 Test endpoint: http://localhost:{port}/api/voice/alert/test")
    logger.info(f"💚 Health endpoint: http://localhost:{port}/api/voice/health")
    app.run(host='127.0.0.1', port=port, debug=True, use_reloader=False)
