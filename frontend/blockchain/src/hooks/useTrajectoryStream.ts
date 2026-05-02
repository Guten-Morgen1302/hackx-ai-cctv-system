import { useState, useEffect, useRef } from 'react';
import type { PositionPoint, BlockchainEvent, TrajectoryData, PositionUpdate } from '../types';

const USE_MOCK = import.meta.env.VITE_USE_MOCK !== "false";
const WS_URL = "ws://localhost:8080/ws/trajectories";
const ZONES = ["ENTRY LOBBY", "CORRIDOR A", "ZONE B", "PARKING ENTRY", "MAIN_HALL", "EXIT GATE", "RESTRICTED AREA"];

export const useTrajectoryStream = (): TrajectoryData => {
  const [positionsById, setPositionsById] = useState<Map<number, PositionPoint[]>>(new Map());
  const [lastSeenById, setLastSeenById] = useState<Map<number, Date>>(new Map());
  const [blockchainEvents, setBlockchainEvents] = useState<BlockchainEvent[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<"mock" | "connected" | "disconnected">(
    USE_MOCK ? "mock" : "disconnected"
  );
  
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (USE_MOCK) {
      const interval = setInterval(() => {
        // Generate 5-20 random track IDs (1-25)
        const activeIds = Array.from({ length: 5 + Math.floor(Math.random() * 15) }, () => 1 + Math.floor(Math.random() * 24));
        
        activeIds.forEach(id => {
          setPositionsById(prev => {
            const currentPoints = prev.get(id) || [];
            
            // Random movement based on last position or start at random
            let lastPoint = currentPoints[currentPoints.length - 1];
            let newX, newY;
            
            if (lastPoint) {
              newX = Math.max(0, Math.min(1, lastPoint.x + (Math.random() - 0.5) * 0.05));
              newY = Math.max(0, Math.min(1, lastPoint.y + (Math.random() - 0.5) * 0.05));
            } else {
              newX = Math.random();
              newY = Math.random();
            }

            const newPoint: PositionPoint = {
              x: newX,
              y: newY,
              zone: ZONES[Math.floor(Math.random() * ZONES.length)],
              timestamp: new Date().toISOString()
            };

            const newMap = new Map(prev);
            newMap.set(id, [...currentPoints.slice(-100), newPoint]); // Keep last 100 points
            return newMap;
          });

          setLastSeenById(prev => {
            const newMap = new Map(prev);
            newMap.set(id, new Date());
            return newMap;
          });
        });

        // Randomly emit blockchain event every few seconds
        if (Math.random() > 0.9) {
          const randomId = activeIds[0];
          const newEvent: BlockchainEvent = {
            event_type: "BLOCKCHAIN_ANCHORED",
            track_id: randomId,
            incident_id: `INC-${Math.random().toString(36).substring(7).toUpperCase()}`,
            tx_hash: "0x" + Array.from({length: 64}, () => Math.floor(Math.random() * 16).toString(16)).join(''),
            timestamp: new Date().toISOString(),
            chain: "Polygon Amoy"
          };
          setBlockchainEvents(prev => [newEvent, ...prev].slice(0, 50));
        }
      }, 400);

      return () => clearInterval(interval);
    } else {
      // Real WebSocket logic
      const connect = () => {
        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => setConnectionStatus("connected");
        ws.onclose = () => {
          setConnectionStatus("disconnected");
          setTimeout(connect, 3000); // Reconnect
        };
        ws.onerror = () => setConnectionStatus("disconnected");

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.event_type === "POSITION_UPDATE") {
              const update = data as PositionUpdate;
              setPositionsById(prev => {
                const currentPoints = prev.get(update.track_id) || [];
                const newMap = new Map(prev);
                newMap.set(update.track_id, [...currentPoints.slice(-100), { x: update.x, y: update.y, zone: update.zone, timestamp: update.timestamp }]);
                return newMap;
              });
              setLastSeenById(prev => {
                const newMap = new Map(prev);
                newMap.set(update.track_id, new Date(update.timestamp));
                return newMap;
              });
            } else if (data.event_type === "BLOCKCHAIN_ANCHORED") {
              setBlockchainEvents(prev => [data as BlockchainEvent, ...prev].slice(0, 50));
            }
          } catch (e) {
            console.error("Error parsing WS message", e);
          }
        };
      };

      connect();
      return () => wsRef.current?.close();
    }
  }, []);

  return {
    positionsById,
    lastSeenById,
    blockchainEvents,
    connectionStatus
  };
};
