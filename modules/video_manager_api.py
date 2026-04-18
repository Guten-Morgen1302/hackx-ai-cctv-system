"""
Video Filter & Management API
Allows dynamic switching between test videos
"""

from flask import Blueprint, jsonify, request
import os
import logging
from pathlib import Path
from modules.video_analytics_data import get_video_analytics, get_all_videos_analytics, get_video_summary

logger = logging.getLogger(__name__)

video_bp = Blueprint('video', __name__, url_prefix='/api/videos')

# Available test videos
AVAILABLE_VIDEOS = [
    "test.mp4",
    "test1.mp4",
    "test3.mp4",
    "test4.mp4",
    "test5.mp4"
]

current_video = "test5.mp4"


@video_bp.route('/available', methods=['GET'])
def get_available_videos():
    """Get list of available video files"""
    try:
        videos_info = []
        for video_name in AVAILABLE_VIDEOS:
            video_path = video_name
            exists = os.path.exists(video_path)
            size = 0
            if exists:
                size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            
            videos_info.append({
                "name": video_name,
                "exists": exists,
                "size_mb": round(size, 2),
                "active": video_name == current_video
            })
        
        return jsonify({
            "success": True,
            "available_videos": videos_info,
            "total": len(videos_info),
            "current_video": current_video
        }), 200
    except Exception as e:
        logger.error(f"Error getting available videos: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@video_bp.route('/current', methods=['GET'])
def get_current_video():
    """Get currently loaded video"""
    return jsonify({
        "success": True,
        "current_video": current_video
    }), 200


@video_bp.route('/switch/<video_name>', methods=['POST'])
def switch_video(video_name):
    """Switch to different video file"""
    global current_video
    try:
        if video_name not in AVAILABLE_VIDEOS:
            return jsonify({
                "success": False,
                "error": f"Video {video_name} not in available list",
                "available": AVAILABLE_VIDEOS
            }), 400
        
        if not os.path.exists(video_name):
            return jsonify({
                "success": False,
                "error": f"Video file not found: {video_name}",
                "path": os.path.abspath(video_name)
            }), 404
        
        current_video = video_name
        logger.info(f"🎬 Switched to video: {video_name}")
        
        return jsonify({
            "success": True,
            "message": f"Switched to {video_name}",
            "current_video": current_video
        }), 200
    except Exception as e:
        logger.error(f"Error switching video: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@video_bp.route('/create-test2', methods=['POST'])
def create_test2():
    """Create test2.mp4 by duplicating test.mp4"""
    try:
        if os.path.exists("test.mp4") and not os.path.exists("test2.mp4"):
            import shutil
            shutil.copy("test.mp4", "test2.mp4")
            logger.info("✅ Created test2.mp4 from test.mp4")
            return jsonify({
                "success": True,
                "message": "test2.mp4 created successfully"
            }), 201
        elif os.path.exists("test2.mp4"):
            return jsonify({
                "success": False,
                "error": "test2.mp4 already exists"
            }), 400
        else:
            return jsonify({
                "success": False,
                "error": "test.mp4 not found"
            }), 404
    except Exception as e:
        logger.error(f"Error creating test2.mp4: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@video_bp.route('/analytics/<video_name>', methods=['GET'])
def get_video_analytics_data(video_name):
    """Get hardcoded analytics for a specific video"""
    try:
        analytics = get_video_analytics(video_name)
        if not analytics:
            return jsonify({
                "success": False,
                "error": f"No analytics found for {video_name}",
                "available_videos": ["test.mp4", "test1.mp4", "test3.mp4", "test4.mp4", "test5.mp4"]
            }), 404
        
        logger.info(f"📊 Retrieved analytics for {video_name}: {analytics['people_detected']} people detected")
        
        return jsonify({
            "success": True,
            "video_name": video_name,
            "analytics": analytics
        }), 200
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@video_bp.route('/analytics/all', methods=['GET'])
def get_all_analytics():
    """Get analytics for all videos"""
    try:
        all_analytics = get_all_videos_analytics()
        return jsonify({
            "success": True,
            "total_videos": len(all_analytics),
            "analytics": all_analytics
        }), 200
    except Exception as e:
        logger.error(f"Error getting all analytics: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@video_bp.route('/current/analytics', methods=['GET'])
def get_current_video_analytics():
    """Get analytics for currently loaded video"""
    try:
        analytics = get_video_analytics(current_video)
        return jsonify({
            "success": True,
            "current_video": current_video,
            "analytics": analytics
        }), 200
    except Exception as e:
        logger.error(f"Error getting current video analytics: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
