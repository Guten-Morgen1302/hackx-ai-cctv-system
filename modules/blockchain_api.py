"""
Flask API Endpoints for Blockchain & Risk Scoring System
Add these endpoints to app.py
"""

from flask import Blueprint, jsonify, request
from modules.blockchain_system import evidence_chain, identity_chain, risk_engine
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create blueprint
blockchain_bp = Blueprint('blockchain', __name__, url_prefix='/api')


# ─────────────────────────────────────────
# EVIDENCE CHAIN ENDPOINTS
# ─────────────────────────────────────────

@blockchain_bp.route('/chain', methods=['GET'])
def get_evidence_chain():
    """Get entire evidence blockchain"""
    try:
        chain_data = evidence_chain.get_chain()
        return jsonify({
            "success": True,
            "total_blocks": len(chain_data),
            "chain": chain_data
        }), 200
    except Exception as e:
        logger.error(f"Error getting chain: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blockchain_bp.route('/chain/verify', methods=['GET'])
def verify_chain():
    """Verify entire chain integrity"""
    try:
        health = evidence_chain.get_chain_health()
        return jsonify({
            "success": True,
            "chain_health": health,
            "verified": health["is_valid"]
        }), 200
    except Exception as e:
        logger.error(f"Error verifying chain: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blockchain_bp.route('/chain/block/<int:index>/verify', methods=['GET'])
def verify_block(index):
    """Verify specific block"""
    try:
        verification = evidence_chain.verify_block(index)
        return jsonify({
            "success": True,
            "verification": verification
        }), 200
    except Exception as e:
        logger.error(f"Error verifying block: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blockchain_bp.route('/chain/add', methods=['POST'])
def add_block():
    """Add new block to chain (called by alert system)"""
    try:
        data = request.json
        event_data = {
            "camera_id": data.get("camera_id"),
            "event_type": data.get("event_type"),
            "person_id": data.get("person_id"),
            "zone": data.get("zone"),
            "severity": data.get("severity"),
            "image_hash": data.get("image_hash")
        }
        
        new_block = evidence_chain.add_block(event_data)
        logger.info(f"✅ New block added: {new_block.hash[:16]}... (event: {data.get('event_type')})")
        
        return jsonify({
            "success": True,
            "block": new_block.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"Error adding block: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ─────────────────────────────────────────
# IDENTITY CHAIN ENDPOINTS
# ─────────────────────────────────────────

@blockchain_bp.route('/identity', methods=['GET'])
def get_identity_registry():
    """Get all enrolled identities"""
    try:
        identities = identity_chain.get_all_identities()
        return jsonify({
            "success": True,
            "total_identities": len(identities),
            "identities": identities
        }), 200
    except Exception as e:
        logger.error(f"Error getting identity registry: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blockchain_bp.route('/identity/enroll', methods=['POST'])
def enroll_person():
    """Enroll new person in identity chain"""
    try:
        data = request.json
        person_data = {
            "person_id": data.get("person_id"),
            "name": data.get("name"),
            "role": data.get("role"),
            "department": data.get("department"),
            "face_encoding_hash": data.get("face_encoding_hash"),
            "access_zones": data.get("access_zones", [])
        }
        
        new_identity = identity_chain.enroll_person(person_data)
        logger.info(f"✅ New identity enrolled: {person_data['name']} ({person_data['person_id']})")
        
        return jsonify({
            "success": True,
            "identity_block": new_identity.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"Error enrolling person: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blockchain_bp.route('/identity/<person_id>', methods=['GET'])
def get_identity(person_id):
    """Get specific person's identity block"""
    try:
        identity = identity_chain.get_person(person_id)
        if not identity:
            return jsonify({"success": False, "error": "Person not found"}), 404
        
        return jsonify({
            "success": True,
            "identity": identity
        }), 200
    except Exception as e:
        logger.error(f"Error getting identity: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blockchain_bp.route('/identity/<person_id>/verify-access', methods=['POST'])
def verify_access(person_id):
    """Verify if person can access zone"""
    try:
        data = request.json
        zone = data.get("zone")
        
        access_result = identity_chain.verify_access(person_id, zone)
        return jsonify({
            "success": True,
            "access_verification": access_result
        }), 200
    except Exception as e:
        logger.error(f"Error verifying access: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ─────────────────────────────────────────
# RISK SCORING ENDPOINTS
# ─────────────────────────────────────────

@blockchain_bp.route('/risk/scores', methods=['GET'])
def get_all_risk_scores():
    """Get all current risk scores"""
    try:
        scores = {}
        for person_id in risk_engine.person_scores:
            breakdown = risk_engine.get_score_breakdown(person_id)
            scores[person_id] = breakdown
        
        return jsonify({
            "success": True,
            "total_persons": len(scores),
            "scores": scores
        }), 200
    except Exception as e:
        logger.error(f"Error getting risk scores: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blockchain_bp.route('/risk/score/<person_id>', methods=['GET'])
def get_risk_score(person_id):
    """Get specific person's risk score"""
    try:
        breakdown = risk_engine.get_score_breakdown(person_id)
        return jsonify({
            "success": True,
            "score_breakdown": breakdown
        }), 200
    except Exception as e:
        logger.error(f"Error getting risk score: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blockchain_bp.route('/risk/high', methods=['GET'])
def get_high_risk_persons():
    """Get all persons with high risk (> 55)"""
    try:
        threshold = request.args.get('threshold', 55, type=int)
        high_risk = risk_engine.get_high_risk_persons(threshold)
        
        return jsonify({
            "success": True,
            "threshold": threshold,
            "high_risk_count": len(high_risk),
            "persons": high_risk
        }), 200
    except Exception as e:
        logger.error(f"Error getting high risk persons: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blockchain_bp.route('/risk/score/<person_id>/update', methods=['POST'])
def update_risk_score(person_id):
    """Update person's risk score with new factors"""
    try:
        data = request.json
        factors = data.get("factors", {})
        
        score = risk_engine.update_score(person_id, factors)
        tier = risk_engine.get_risk_tier(score)
        
        logger.info(f"⚠️ Risk score updated: {person_id} = {score:.1f} ({tier})")
        
        return jsonify({
            "success": True,
            "person_id": person_id,
            "score": score,
            "risk_tier": tier
        }), 200
    except Exception as e:
        logger.error(f"Error updating risk score: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blockchain_bp.route('/risk/history/<person_id>', methods=['GET'])
def get_risk_history(person_id):
    """Get person's risk score history"""
    try:
        history = risk_engine.person_history.get(person_id, [])
        
        return jsonify({
            "success": True,
            "person_id": person_id,
            "history_count": len(history),
            "history": history[-100:] if len(history) > 100 else history  # Last 100 records
        }), 200
    except Exception as e:
        logger.error(f"Error getting risk history: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blockchain_bp.route('/health', methods=['GET'])
def get_system_health():
    """Get overall system health (blockchain + risk engine)"""
    try:
        chain_health = evidence_chain.get_chain_health()
        high_risk_count = len(risk_engine.get_high_risk_persons())
        
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "blockchain": chain_health,
            "high_risk_persons": high_risk_count,
            "total_tracked_persons": len(risk_engine.person_scores)
        }), 200
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
