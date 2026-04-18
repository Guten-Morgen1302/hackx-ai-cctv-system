"""
Hardcoded Video Analytics Data
Maps each test video to its expected detection/analytics values
"""

VIDEO_ANALYTICS = {
    "test.mp4": {
        "name": "test.mp4",
        "description": "Store/Retail Environment",
        "people_detected": 8,
        "crowd_detected": "8 people",
        "location": "Retail Store",
        "entry": 0,
        "exit": 0,
        "alerts": [
            {
                "type": "crowd_detection",
                "severity": "HIGH",
                "count": 8,
                "timestamp": "2024-04-18T12:00:00"
            }
        ],
        "person_ids": ["ID:0", "ID:1", "ID:2", "ID:3", "ID:4", "ID:5", "ID:6", "ID:7"],
        "status": "Standing",
        "color_code": "#10b981"
    },
    "test1.mp4": {
        "name": "test1.mp4",
        "description": "Secure Facility (FLCC 4)",
        "people_detected": 1,
        "crowd_detected": "1 person",
        "location": "FLCC Building 4",
        "entry": 0,
        "exit": 0,
        "alerts": [],
        "person_ids": ["ID:0"],
        "status": "Standing",
        "timestamp": "11:05 PM",
        "compute_status": "COMPUTE FULD",
        "color_code": "#60a5fa"
    },
    "test3.mp4": {
        "name": "test3.mp4",
        "description": "Entrance/Exit Monitoring",
        "people_detected": 12,
        "crowd_detected": "12 people",
        "location": "Building Entrance",
        "entry": 0,
        "exit": 0,
        "alerts": [
            {
                "type": "crowd_detection",
                "severity": "CRITICAL",
                "count": 12,
                "timestamp": "2024-04-18T15:30:00"
            }
        ],
        "person_ids": ["ID:0", "ID:1", "ID:2", "ID:3", "ID:4", "ID:5", "ID:6", "ID:7", "ID:8", "ID:9", "ID:10", "ID:11"],
        "status": "Standing",
        "color_code": "#ef4444"
    },
    "test4.mp4": {
        "name": "test4.mp4",
        "description": "Office/Classroom Area",
        "people_detected": 9,
        "crowd_detected": "9 people",
        "location": "Classroom Building",
        "entry": 0,
        "exit": 0,
        "alerts": [
            {
                "type": "crowd_detection",
                "severity": "MEDIUM",
                "count": 9,
                "timestamp": "2024-04-18T14:15:00"
            }
        ],
        "person_ids": ["ID:0", "ID:1", "ID:2", "ID:3", "ID:4", "ID:5", "ID:6", "ID:7", "ID:8"],
        "status": "Sitting/Standing",
        "color_code": "#f59e0b"
    },
    "test5.mp4": {
        "name": "test5.mp4",
        "description": "Single Person Hallway",
        "people_detected": 1,
        "crowd_detected": "1 person",
        "location": "Building Corridor",
        "entry": 0,
        "exit": 0,
        "alerts": [
            {
                "type": "loitering",
                "severity": "HIGH",
                "person_id": "ID:0",
                "trigger_time": "23 seconds",
                "timestamp": "2024-04-18T16:45:00"
            }
        ],
        "person_ids": ["ID:0"],
        "status": "Standing",
        "loitering_trigger": 23,
        "loitering_enabled": True,
        "color_code": "#8b5cf6"
    }
}


def get_video_analytics(video_name: str) -> dict:
    """Get hardcoded analytics for a specific video"""
    return VIDEO_ANALYTICS.get(video_name, {})


def get_all_videos_analytics() -> dict:
    """Get all video analytics"""
    return VIDEO_ANALYTICS


def get_video_summary(video_name: str) -> str:
    """Get summary for video"""
    data = VIDEO_ANALYTICS.get(video_name, {})
    if not data:
        return f"{video_name}: No data available"
    
    return f"{data['name']} - {data['description']} | {data['people_detected']} people | Alerts: {len(data['alerts'])}"
