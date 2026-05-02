import React from 'react';

interface IdListPanelProps {
  ids: number[];
  selectedId: number | null;
  onSelectId: (id: number | null) => void;
  lastSeen: Map<number, Date>;
  zones: Map<number, string>;
}

export const IdListPanel: React.FC<IdListPanelProps> = ({ ids, selectedId, onSelectId, lastSeen, zones }) => {
  return (
    <div className="w-64 h-full hacker-panel border-l-0 border-y-0 flex flex-col z-10 overflow-hidden">
      <div className="p-4 border-b border-white/10 flex items-center justify-between">
        <h2 className="text-xs font-black uppercase tracking-widest text-gray-400">Active Identities</h2>
        <span className="text-[10px] bg-hacker-red/20 text-hacker-red px-2 py-0.5 rounded-full font-bold border border-hacker-red/30">
          {ids.length}
        </span>
      </div>
      
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        <button
          onClick={() => onSelectId(null)}
          className={`w-full p-3 rounded-lg text-left transition-all border ${
            selectedId === null 
              ? 'bg-white/5 border-neon-cyan/50 text-neon-cyan shadow-[inset_0_0_10px_rgba(0,246,255,0.1)]' 
              : 'border-transparent text-gray-500 hover:bg-white/5'
          }`}
        >
          <div className="text-[10px] font-black uppercase tracking-widest">Global View</div>
          <div className="text-xs font-bold mt-0.5">Show All Trajectories</div>
        </button>

        <div className="h-px bg-white/5 mx-2 my-2"></div>

        {ids.sort((a,b) => a-b).map(id => (
          <button
            key={id}
            onClick={() => onSelectId(id)}
            className={`w-full p-3 rounded-lg text-left transition-all border group ${
              selectedId === id 
                ? 'bg-hacker-red/10 border-hacker-red/50 text-hacker-red shadow-[inset_0_0_10px_rgba(255,32,64,0.1)]' 
                : 'border-transparent text-gray-400 hover:bg-white/5'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className={`text-sm font-black ${selectedId === id ? 'text-hacker-red' : 'text-white'}`}>
                ID: {id.toString().padStart(2, '0')}
              </span>
              <div className={`text-[8px] font-bold px-1.5 py-0.5 rounded uppercase tracking-tighter ${
                selectedId === id ? 'bg-hacker-red/30 text-white' : 'bg-gray-800 text-gray-500 group-hover:bg-gray-700'
              }`}>
                Tracking
              </div>
            </div>
            
            <div className="mt-2 space-y-1">
              <div className="flex items-center space-x-1.5">
                <div className="w-1 h-1 rounded-full bg-neon-cyan"></div>
                <span className="text-[10px] font-bold uppercase truncate opacity-70">
                  {zones.get(id) || 'UNKNOWN_ZONE'}
                </span>
              </div>
              <div className="text-[9px] opacity-40 font-bold uppercase flex items-center space-x-1">
                <span>Last Activity:</span>
                <span>{lastSeen.get(id)?.toLocaleTimeString([], { hour12: false }) || '--:--:--'}</span>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};
