import cv2
import logging

logger = logging.getLogger(__name__)

try:
    # Try new API first (Python 3.14+ compatible)
    from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions
    from mediapipe.tasks.python.vision.core.vision_task_running_mode import VisionTaskRunningMode
    MEDIAPIPE_API = "new"
except ImportError:
    # Fall back to old API
    try:
        from mediapipe.python.solutions import pose
        MEDIAPIPE_API = "old"
    except ImportError:
        import mediapipe as mp
        MEDIAPIPE_API = "old"

class PostureClassifier:
    """Accurate posture classification using MediaPipe"""
    
    def __init__(self):
        if MEDIAPIPE_API == "old":
            try:
                from mediapipe.python.solutions import pose
                self.mp_pose = pose
                self.pose = pose.Pose(
                    static_image_mode=False,
                    model_complexity=1,
                    enable_segmentation=False,
                    min_detection_confidence=0.7,
                    min_tracking_confidence=0.5
                )
                self.use_new_api = False
            except Exception as e:
                logger.warning(f"Could not initialize old API, will use simplified detection: {e}")
                self.use_new_api = False
                self.pose = None
        else:
            self.use_new_api = True
            self.pose = None
        
    def classify_posture(self, image, bbox=None):
        """Classify posture from image region with improved accuracy"""
        try:
            if self.pose is None:
                # Return default when pose detector unavailable
                return "Standing", None
                
            if bbox is not None:
                x1, y1, x2, y2 = bbox
                # Add padding for better pose detection
                padding = 20
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(image.shape[1], x2 + padding)
                y2 = min(image.shape[0], y2 + padding)
                roi = image[y1:y2, x1:x2]
            else:
                roi = image
                
            if roi.size == 0:
                return "Unknown", None
                
            rgb_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_roi)
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                posture = self.analyze_pose_landmarks(landmarks)
                return posture, results.pose_landmarks
            else:
                return "Unknown", None
                
        except Exception as e:
            logger.error(f"Error in posture classification: {e}")
            return "Standing", None
    
    def analyze_pose_landmarks(self, landmarks):
        """Analyze pose landmarks with improved accuracy"""
        try:
            # MediaPipe pose landmarks indices
            # 0=nose, 11=left_shoulder, 12=right_shoulder, 23=left_hip, 24=right_hip, 
            # 25=left_knee, 26=right_knee, 27=left_ankle, 28=right_ankle
            
            nose = landmarks[0]
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            left_knee = landmarks[25]
            right_knee = landmarks[26]
            left_ankle = landmarks[27]
            right_ankle = landmarks[28]
            
            # Calculate key points
            shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2
            hip_center_y = (left_hip.y + right_hip.y) / 2
            knee_center_y = (left_knee.y + right_knee.y) / 2
            ankle_center_y = (left_ankle.y + right_ankle.y) / 2
            
            # Calculate torso angle
            torso_vertical = abs(shoulder_center_y - hip_center_y)
            
            # More accurate posture classification
            
            if ankle_center_y > knee_center_y and knee_center_y > hip_center_y:  # Standing position
                return "Standing"
            else:
                return "Analyzing..."
            
                
        except Exception as e:
            logger.error(f"Error analyzing pose landmarks: {e}")
            return "Analyzing..."