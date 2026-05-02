export interface PositionPoint {
  x: number;
  y: number;
  zone: string;
  timestamp: string;
}

export interface PositionUpdate {
  event_type: "POSITION_UPDATE";
  track_id: number;
  x: number;
  y: number;
  zone: string;
  timestamp: string;
}

export interface BlockchainEvent {
  event_type: "BLOCKCHAIN_ANCHORED";
  track_id: number;
  incident_id: string;
  tx_hash: string;
  timestamp: string;
  chain: string;
}

export interface FraudRingEvent {
  event_type: "FRAUD_RING_DETECTED";
  nodes: string[];
  risk_score: number;
  timestamp: string;
}

export type TrajectoryEvent = PositionUpdate | BlockchainEvent | FraudRingEvent;

export interface TrajectoryData {
  positionsById: Map<number, PositionPoint[]>;
  lastSeenById: Map<number, Date>;
  blockchainEvents: BlockchainEvent[];
  connectionStatus: "mock" | "connected" | "disconnected";
}
