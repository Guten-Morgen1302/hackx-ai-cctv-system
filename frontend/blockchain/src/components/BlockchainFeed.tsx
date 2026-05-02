import React, { useEffect, useRef, useState } from 'react';
import type { BlockchainEvent, PositionPoint } from '../types';

interface BlockchainFeedProps {
  events: BlockchainEvent[];
  positions: Map<number, PositionPoint[]>;
}

export const BlockchainFeed: React.FC<BlockchainFeedProps> = ({ events, positions }) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [filter, setFilter] = useState<'all' | 'blockchain'>('all');

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0;
    }
  }, [events, positions]);

  // Combine and sort events for display
  const displayItems = React.useMemo(() => {
    const items: { type: 'pos' | 'block', data: any, ts: string }[] = [];
    
    if (filter === 'all') {
      positions.forEach((points, id) => {
        const last = points[points.length - 1];
        items.push({
          type: 'pos',
          data: { id, x: last.x, y: last.y, zone: last.zone },
          ts: last.timestamp
        });
      });
    }

    events.forEach(e => {
      items.push({
        type: 'block',
        data: e,
        ts: e.timestamp
      });
    });

    return items.sort((a, b) => new Date(b.ts).getTime() - new Date(a.ts).getTime()).slice(0, 50);
  }, [events, positions, filter]);

  return (
    <div className="w-80 h-full hacker-panel border-r-0 border-y-0 flex flex-col z-10 overflow-hidden">
      <div className="p-4 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="w-1 h-1 rounded-full bg-hacker-red animate-ping"></div>
          <h2 className="text-xs font-black uppercase tracking-widest text-hacker-red">Live Event Feed</h2>
        </div>
        
        <select 
          value={filter}
          onChange={(e) => setFilter(e.target.value as any)}
          className="bg-black/50 border border-white/10 rounded text-[9px] font-black uppercase px-1 py-0.5 text-gray-400 outline-none hover:border-hacker-red/50 transition-colors"
        >
          <option value="all">All Events</option>
          <option value="blockchain">Only Blocks</option>
        </select>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth">
        {displayItems.map((item, idx) => {
          const time = new Date(item.ts).toLocaleTimeString([], { hour12: false });
          
          if (item.type === 'pos') {
            return (
              <div key={`pos-${idx}`} className="flex space-x-3 opacity-60">
                <span className="text-[10px] text-gray-600 font-bold shrink-0">[{time}]</span>
                <div className="text-[10px] font-bold leading-relaxed">
                  <span className="text-neon-cyan">[Track {item.data.id}]</span> Position 
                  <span className="text-white/80"> ({item.data.x.toFixed(2)}, {item.data.y.toFixed(2)}) </span> 
                  in <span className="text-neon-cyan/80">{item.data.zone}</span>
                </div>
              </div>
            );
            return (
              <div key={`block-${idx}`} className={`border p-2 rounded-md space-y-1 relative overflow-hidden group ${
                item.data.event_type === 'FRAUD_RING_DETECTED' ? 'bg-orange-500/10 border-orange-500/30' : 'bg-hacker-red/5 border-hacker-red/20'
              }`}>
                <div className={`absolute top-0 left-0 w-1 h-full opacity-50 ${
                  item.data.event_type === 'FRAUD_RING_DETECTED' ? 'bg-orange-500' : 'bg-hacker-red'
                }`}></div>
                
                <div className="flex justify-between items-start">
                  <span className={`text-[10px] font-black uppercase tracking-widest ${
                    item.data.event_type === 'FRAUD_RING_DETECTED' ? 'text-orange-500' : 'text-hacker-red'
                  }`}>
                    [{item.data.event_type === 'FRAUD_RING_DETECTED' ? 'Graph Alert' : 'Blockchain Log'}]
                  </span>
                  <span className="text-[9px] text-gray-500 font-bold">{time}</span>
                </div>

                {item.data.event_type === 'FRAUD_RING_DETECTED' ? (
                  <div className="text-[10px] font-bold leading-relaxed">
                    <span className="text-white/90">GNN detect fraud ring: </span>
                    <span className="text-orange-400">{item.data.nodes.join(', ')}</span>
                    <div className="text-[9px] text-orange-500/80 mt-1 uppercase font-black">
                      RISK PROBABILITY: {(item.data.risk_score * 100).toFixed(1)}%
                    </div>
                  </div>
                ) : (
                  <div className="text-[10px] font-bold leading-relaxed">
                    <span className="text-white/90">Anchored trajectory hash for Track {item.data.track_id}: </span>
                    <span className="text-hacker-red/90 break-all">{item.data.tx_hash.substring(0, 16)}...</span>
                  </div>
                )}

                <div className="text-[8px] text-gray-500 font-black uppercase flex items-center space-x-2 pt-1 border-t border-white/5">
                  <span className={item.data.event_type === 'FRAUD_RING_DETECTED' ? 'text-orange-500/50' : 'text-hacker-red/50'}>
                    {item.data.event_type === 'FRAUD_RING_DETECTED' ? 'NETWORK_FRAUD' : `INCIDENT: ${item.data.incident_id}`}
                  </span>
                  <span className="opacity-30">•</span>
                  <span>{item.data.event_type === 'FRAUD_RING_DETECTED' ? 'GRAPH_ENGINE' : item.data.chain}</span>
                </div>
              </div>
            );
        })}
      </div>
      
      <div className="p-3 border-t border-white/5 bg-black/20 text-[8px] font-black uppercase text-gray-600 flex justify-between">
        <span>Displaying {displayItems.length} entries</span>
        <button className="hover:text-hacker-red transition-colors">↓ Resume Auto-scroll</button>
      </div>
    </div>
  );
};
