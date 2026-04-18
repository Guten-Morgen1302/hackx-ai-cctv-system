"""
Blockchain-Based Identity & Evidence Integrity System
Combines blockchain evidence chain with risk scoring and identity registry
"""

import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading
from pathlib import Path


class Block:
    """Individual block in the blockchain"""
    
    def __init__(self, index: int, timestamp: str, event_data: Dict, prev_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.event_data = event_data  # {camera_id, event_type, person_id, zone, severity, image_hash}
        self.prev_hash = prev_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of this block"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "event_data": self.event_data,
            "prev_hash": self.prev_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "event_data": self.event_data,
            "prev_hash": self.prev_hash,
            "hash": self.hash
        }


class IdentityBlock:
    """Block for person identity in the identity chain"""
    
    def __init__(self, person_id: str, name: str, role: str, department: str, 
                 face_encoding_hash: str, access_zones: List[str], prev_hash: str):
        self.person_id = person_id
        self.name = name
        self.role = role
        self.department = department
        self.face_encoding_hash = face_encoding_hash
        self.access_zones = access_zones
        self.enrollment_timestamp = datetime.now().isoformat()
        self.prev_hash = prev_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of this identity block"""
        block_string = json.dumps({
            "person_id": self.person_id,
            "name": self.name,
            "role": self.role,
            "department": self.department,
            "face_encoding_hash": self.face_encoding_hash,
            "access_zones": self.access_zones,
            "enrollment_timestamp": self.enrollment_timestamp,
            "prev_hash": self.prev_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        return {
            "person_id": self.person_id,
            "name": self.name,
            "role": self.role,
            "department": self.department,
            "face_encoding_hash": self.face_encoding_hash,
            "access_zones": self.access_zones,
            "enrollment_timestamp": self.enrollment_timestamp,
            "prev_hash": self.prev_hash,
            "hash": self.hash
        }


class BlockChain:
    """Local blockchain for evidence integrity"""
    
    def __init__(self, data_dir: str = "logs/blockchain"):
        self.chain: List[Block] = []
        self.data_dir = data_dir
        self.chain_file = os.path.join(data_dir, "evidence_chain.json")
        self.lock = threading.Lock()
        
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        self._load_chain()
    
    def _load_chain(self):
        """Load chain from JSON file"""
        if os.path.exists(self.chain_file):
            try:
                with open(self.chain_file, 'r') as f:
                    chain_data = json.load(f)
                    for block_data in chain_data:
                        block = Block(
                            block_data["index"],
                            block_data["timestamp"],
                            block_data["event_data"],
                            block_data["prev_hash"]
                        )
                        self.chain.append(block)
            except Exception as e:
                print(f"Error loading chain: {e}")
    
    def _save_chain(self):
        """Save chain to JSON file"""
        try:
            with open(self.chain_file, 'w') as f:
                json.dump([block.to_dict() for block in self.chain], f, indent=2)
        except Exception as e:
            print(f"Error saving chain: {e}")
    
    def add_block(self, event_data: Dict) -> Block:
        """Add new block to chain"""
        with self.lock:
            prev_hash = self.chain[-1].hash if self.chain else "0"
            new_block = Block(
                len(self.chain),
                datetime.now().isoformat(),
                event_data,
                prev_hash
            )
            self.chain.append(new_block)
            self._save_chain()
            return new_block
    
    def verify_chain(self) -> bool:
        """Verify entire chain integrity"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            prev_block = self.chain[i - 1]
            
            # Verify previous hash
            if current_block.prev_hash != prev_block.hash:
                return False
            
            # Verify current hash
            if current_block.hash != current_block.calculate_hash():
                return False
        
        return True
    
    def verify_block(self, index: int) -> Dict:
        """Verify specific block"""
        if index >= len(self.chain):
            return {"verified": False, "error": "Block not found"}
        
        block = self.chain[index]
        current_hash = block.calculate_hash()
        
        return {
            "verified": current_hash == block.hash,
            "index": index,
            "block_hash": block.hash,
            "calculated_hash": current_hash,
            "timestamp": block.timestamp,
            "event_type": block.event_data.get("event_type")
        }
    
    def get_chain(self) -> List[Dict]:
        """Get entire chain as list of dicts"""
        return [block.to_dict() for block in self.chain]
    
    def get_chain_health(self) -> Dict:
        """Get chain health status"""
        is_valid = self.verify_chain()
        return {
            "total_blocks": len(self.chain),
            "integrity": "100%" if is_valid else "COMPROMISED",
            "is_valid": is_valid,
            "genesis_block": self.chain[0].timestamp if self.chain else None,
            "last_block": self.chain[-1].timestamp if self.chain else None,
            "verified_at": datetime.now().isoformat()
        }


class IdentityChain:
    """Local blockchain for identity registry"""
    
    def __init__(self, data_dir: str = "logs/blockchain"):
        self.chain: List[IdentityBlock] = []
        self.data_dir = data_dir
        self.chain_file = os.path.join(data_dir, "identity_chain.json")
        self.lock = threading.Lock()
        
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        self._load_chain()
    
    def _load_chain(self):
        """Load identity chain from JSON file"""
        if os.path.exists(self.chain_file):
            try:
                with open(self.chain_file, 'r') as f:
                    chain_data = json.load(f)
                    for block_data in chain_data:
                        block = IdentityBlock(
                            block_data["person_id"],
                            block_data["name"],
                            block_data["role"],
                            block_data["department"],
                            block_data["face_encoding_hash"],
                            block_data["access_zones"],
                            block_data["prev_hash"]
                        )
                        self.chain.append(block)
            except Exception as e:
                print(f"Error loading identity chain: {e}")
    
    def _save_chain(self):
        """Save identity chain to JSON file"""
        try:
            with open(self.chain_file, 'w') as f:
                json.dump([block.to_dict() for block in self.chain], f, indent=2)
        except Exception as e:
            print(f"Error saving identity chain: {e}")
    
    def enroll_person(self, person_data: Dict) -> IdentityBlock:
        """Enroll new person to identity chain"""
        with self.lock:
            prev_hash = self.chain[-1].hash if self.chain else "0"
            block = IdentityBlock(
                person_data["person_id"],
                person_data["name"],
                person_data["role"],
                person_data["department"],
                person_data["face_encoding_hash"],
                person_data["access_zones"],
                prev_hash
            )
            self.chain.append(block)
            self._save_chain()
            return block
    
    def get_person(self, person_id: str) -> Optional[Dict]:
        """Get person's identity block"""
        for block in self.chain:
            if block.person_id == person_id:
                return block.to_dict()
        return None
    
    def get_all_identities(self) -> List[Dict]:
        """Get all enrolled identities"""
        return [block.to_dict() for block in self.chain]
    
    def verify_access(self, person_id: str, zone: str) -> Dict:
        """Verify if person can access zone"""
        person = self.get_person(person_id)
        if not person:
            return {"authorized": False, "reason": "Person not found"}
        
        authorized = zone in person["access_zones"]
        return {
            "authorized": authorized,
            "person_id": person_id,
            "zone": zone,
            "allowed_zones": person["access_zones"],
            "timestamp": datetime.now().isoformat()
        }


class RiskScoreEngine:
    """Predictive threat risk scoring system"""
    
    # Risk thresholds
    RISK_TIERS = {
        "LOW": (0, 30),
        "MEDIUM": (31, 55),
        "HIGH": (56, 75),
        "CRITICAL": (76, 100)
    }
    
    # Behavior factors (increase score)
    BEHAVIOR_WEIGHTS = {
        "restricted_zone_time": 30,      # Max +30
        "loitering_per_min": 5,           # +5 per min
        "restricted_zone_visit": 25,      # +25
        "abandoned_object": 20,           # +20
        "movement_speed": 10,             # +10
        "repeated_return": 5,             # +5 per visit
        "non_operating_hours": 20,        # +20
        "suspicious_posture": 15,         # +15 (crouching)
        "near_asset_zone": 15,            # +15
        "following_person": 20            # +20
    }
    
    # Trust factors (decrease score)
    TRUST_WEIGHTS = {
        "staff_recognized": -25,
        "student_recognized": -15,
        "normal_speed": -5,
        "id_verified": -20,
        "authorized_access": -10
    }
    
    def __init__(self):
        self.person_scores: Dict[str, float] = {}
        self.person_history: Dict[str, List[Dict]] = {}
        self.person_metadata: Dict[str, Dict] = {}
        self.lock = threading.Lock()
    
    def update_score(self, person_id: str, factors: Dict[str, Any]) -> float:
        """Update risk score for person based on factors"""
        with self.lock:
            current_score = self.person_scores.get(person_id, 0)
            
            # Apply behavior factors (positive)
            for factor, value in factors.items():
                if factor in self.BEHAVIOR_WEIGHTS:
                    if isinstance(value, bool):
                        if value:
                            current_score += self.BEHAVIOR_WEIGHTS[factor]
                    else:
                        current_score += value * self.BEHAVIOR_WEIGHTS.get(factor, 1)
                elif factor in self.TRUST_WEIGHTS:
                    if isinstance(value, bool):
                        if value:
                            current_score += self.TRUST_WEIGHTS[factor]
                    else:
                        current_score += value * self.TRUST_WEIGHTS.get(factor, 1)
            
            # Clamp score 0-100
            current_score = max(0, min(100, current_score))
            self.person_scores[person_id] = current_score
            
            # Record in history
            if person_id not in self.person_history:
                self.person_history[person_id] = []
            
            self.person_history[person_id].append({
                "timestamp": datetime.now().isoformat(),
                "score": current_score,
                "factors": factors
            })
            
            return current_score
    
    def apply_temporal_decay(self, person_id: str, minutes_passed: int) -> float:
        """Apply temporal decay (5pts per minute, max 10pts/min if absent)"""
        with self.lock:
            if person_id not in self.person_scores:
                return 0
            
            decay = minutes_passed * 5  # 5 points per minute
            if person_id not in self.person_metadata:
                decay = minutes_passed * 10  # 10 points per minute if absent
            
            current_score = self.person_scores[person_id]
            new_score = max(0, current_score - decay)
            self.person_scores[person_id] = new_score
            
            return new_score
    
    def get_score(self, person_id: str) -> float:
        """Get current risk score"""
        return self.person_scores.get(person_id, 0)
    
    def get_risk_tier(self, score: float) -> str:
        """Get risk tier from score"""
        for tier, (min_score, max_score) in self.RISK_TIERS.items():
            if min_score <= score <= max_score:
                return tier
        return "LOW"
    
    def get_score_breakdown(self, person_id: str) -> Dict:
        """Get detailed score breakdown"""
        score = self.person_scores.get(person_id, 0)
        tier = self.get_risk_tier(score)
        
        history = self.person_history.get(person_id, [])
        trend = "stable"
        if len(history) > 1:
            if history[-1]["score"] > history[-2]["score"]:
                trend = "rising"
            elif history[-1]["score"] < history[-2]["score"]:
                trend = "falling"
        
        return {
            "person_id": person_id,
            "score": score,
            "risk_tier": tier,
            "trend": trend,
            "history_count": len(history),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_high_risk_persons(self, threshold: int = 55) -> List[Dict]:
        """Get all persons with score > threshold"""
        high_risk = []
        for person_id, score in self.person_scores.items():
            if score > threshold:
                high_risk.append({
                    "person_id": person_id,
                    "score": score,
                    "risk_tier": self.get_risk_tier(score)
                })
        return sorted(high_risk, key=lambda x: x["score"], reverse=True)
    
    def detect_following(self, person_a_id: str, person_b_id: str, 
                        distance: float, duration_seconds: float) -> bool:
        """Detect if person A is following person B"""
        if distance < 100 and duration_seconds > 30:
            self.update_score(person_a_id, {"following_person": True})
            return True
        return False


# Initialize global instances
evidence_chain = BlockChain()
identity_chain = IdentityChain()
risk_engine = RiskScoreEngine()


def initialize_demo_data():
    """Initialize blockchain with impressive demo data for judges showcase"""
    global evidence_chain, identity_chain, risk_engine
    
    # Only initialize if empty
    if len(evidence_chain.get_chain()) > 0:
        return
    
    # ===== ADD IDENTITIES =====
    demo_persons = [
        {"person_id": "P001", "name": "John Smith", "role": "Security Staff", "department": "Security", "face_encoding_hash": hashlib.sha256(b"P001_face").hexdigest(), "access_zones": ["entry", "exit", "corridor"]},
        {"person_id": "P002", "name": "Unknown Suspect", "role": "Unverified", "department": "Unknown", "face_encoding_hash": hashlib.sha256(b"P002_face").hexdigest(), "access_zones": []},
        {"person_id": "P003", "name": "Sarah Johnson", "role": "Staff", "department": "Admin", "face_encoding_hash": hashlib.sha256(b"P003_face").hexdigest(), "access_zones": ["admin", "hallway"]},
        {"person_id": "P004", "name": "Mike Chen", "role": "Visitor", "department": "Vendor", "face_encoding_hash": hashlib.sha256(b"P004_face").hexdigest(), "access_zones": ["lobby"]},
        {"person_id": "P005", "name": "Unauthorized Person", "role": "Threat", "department": "Unknown", "face_encoding_hash": hashlib.sha256(b"P005_face").hexdigest(), "access_zones": []},
    ]
    
    for person in demo_persons:
        identity_chain.enroll_person(person)
    
    # ===== ADD EVIDENCE INCIDENTS =====
    now = datetime.now()
    incidents = [
        # Critical incidents
        {
            "timestamp": (now - timedelta(minutes=45)).isoformat(),
            "event_type": "loitering_detected",
            "person_id": "P002",
            "zone": "restricted_hallway",
            "severity": "CRITICAL",
            "description": "Unauthorized person loitering in restricted area for 28 seconds"
        },
        {
            "timestamp": (now - timedelta(minutes=40)).isoformat(),
            "event_type": "unauthorized_zone_entry",
            "person_id": "P005",
            "zone": "server_room",
            "severity": "CRITICAL",
            "description": "Unauthorized entry detected in server room - access denied"
        },
        # High severity incidents
        {
            "timestamp": (now - timedelta(minutes=35)).isoformat(),
            "event_type": "aggressive_posture",
            "person_id": "P002",
            "zone": "main_lobby",
            "severity": "HIGH",
            "description": "Aggressive posture detected - potential threat"
        },
        {
            "timestamp": (now - timedelta(minutes=30)).isoformat(),
            "event_type": "crowd_gathering",
            "person_id": "P004",
            "zone": "entrance",
            "severity": "HIGH",
            "description": "Unusual crowd gathering at main entrance - 12 persons detected"
        },
        # Medium severity incidents
        {
            "timestamp": (now - timedelta(minutes=20)).isoformat(),
            "event_type": "motion_detected",
            "person_id": "P001",
            "zone": "security_office",
            "severity": "MEDIUM",
            "description": "Motion detected after hours - verified by staff"
        },
        {
            "timestamp": (now - timedelta(minutes=15)).isoformat(),
            "event_type": "zone_crossing",
            "person_id": "P003",
            "zone": "hallway_to_admin",
            "severity": "MEDIUM",
            "description": "Authorized staff crossing between zones"
        },
        {
            "timestamp": (now - timedelta(minutes=10)).isoformat(),
            "event_type": "suspicious_behavior",
            "person_id": "P004",
            "zone": "parking_level_2",
            "severity": "HIGH",
            "description": "Suspicious behavior - loitering near vehicles"
        },
        # Recent incidents
        {
            "timestamp": (now - timedelta(minutes=5)).isoformat(),
            "event_type": "motion_detected",
            "person_id": "P001",
            "zone": "front_entrance",
            "severity": "LOW",
            "description": "Normal motion - authorized personnel"
        },
    ]
    
    for incident in incidents:
        event_data = {
            "camera_id": f"CAM_{incident['zone'].upper()}",
            "event_type": incident["event_type"],
            "person_id": incident["person_id"],
            "zone": incident["zone"],
            "severity": incident["severity"],
            "description": incident["description"],
            "image_hash": hashlib.sha256(incident["description"].encode()).hexdigest()[:16],
            "timestamp": incident["timestamp"]
        }
        evidence_chain.add_block(event_data)
    
    # ===== ADD RISK SCORES =====
    # Directly set demo risk scores for impressive display
    risk_engine.person_scores = {
        "P001": 15,    # 🟢 LOW - Staff (authorized, verified)
        "P002": 87,    # 🔴 CRITICAL - Unknown loitering in restricted area
        "P003": 12,    # 🟢 LOW - Staff (normal access)
        "P004": 65,    # 🟠 HIGH - Visitor with suspicious behavior
        "P005": 95,    # 🔴 CRITICAL - Unauthorized access attempt
    }
    
    # Add person metadata for context
    risk_engine.person_metadata = {
        "P001": {"name": "John Smith", "role": "Security", "last_seen": "now"},
        "P002": {"name": "Unknown", "role": "Unverified", "last_seen": "45min ago"},
        "P003": {"name": "Sarah Johnson", "role": "Staff", "last_seen": "15min ago"},
        "P004": {"name": "Mike Chen", "role": "Visitor", "last_seen": "10min ago"},
        "P005": {"name": "Unauthorized", "role": "Threat", "last_seen": "5min ago"},
    }
    
    # Add history for each person
    for person_id in risk_engine.person_scores.keys():
        risk_engine.person_history[person_id] = [{
            "timestamp": now.isoformat(),
            "score": risk_engine.person_scores[person_id],
            "factors": {"demo": True}
        }]
    
    print("✅ Demo data initialized successfully!")
