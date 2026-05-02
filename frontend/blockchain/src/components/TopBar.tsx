import React from 'react';

interface TopBarProps {
  connectionStatus: "mock" | "connected" | "disconnected";
  activeCount: number;
}

export const TopBar: React.FC<TopBarProps> = ({ connectionStatus, activeCount }) => {
  return (
    <div className="h-16 hacker-panel border-x-0 border-t-0 px-6 flex items-center justify-between z-20">
      <div className="flex items-center space-x-6">
        <div>
          <h1 className="text-xl font-black tracking-tighter text-white uppercase italic">
            Secure<span className="text-hacker-red">Vista</span>
          </h1>
          <p className="text-[10px] text-gray-500 font-bold uppercase tracking-[0.2em]">
            On-Chain Trajectory Console
          </p>
        </div>
        
        <div className="h-8 w-px bg-white/10 hidden md:block"></div>
        
        <div className="hidden md:flex flex-col">
          <span className="text-[10px] text-gray-500 font-bold uppercase">Network Status</span>
          <span className="text-xs text-neon-cyan font-bold tracking-wider">Polygon Amoy (Testnet)</span>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 bg-black/40 px-3 py-1.5 rounded-full border border-white/5">
          <div className={`w-2 h-2 rounded-full animate-pulse ${
            connectionStatus === 'connected' ? 'bg-neon-green shadow-[0_0_8px_#39ff14]' : 
            connectionStatus === 'mock' ? 'bg-neon-cyan shadow-[0_0_8px_#00f6ff]' : 
            'bg-hacker-red shadow-[0_0_8px_#ff2040]'
          }`}></div>
          <span className={`text-[10px] font-black uppercase tracking-widest ${
            connectionStatus === 'connected' ? 'text-neon-green' : 
            connectionStatus === 'mock' ? 'text-neon-cyan' : 
            'text-hacker-red'
          }`}>
            {connectionStatus}
          </span>
        </div>
        
        <div className="h-8 w-px bg-white/10"></div>
        
        <div className="flex flex-col items-end">
          <span className="text-[10px] text-gray-500 font-bold uppercase">Active Tracking</span>
          <span className="text-xs text-white font-bold">{activeCount} IDs monitored</span>
        </div>
      </div>
    </div>
  );
};
