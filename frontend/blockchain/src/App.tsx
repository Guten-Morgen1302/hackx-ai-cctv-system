import { useState } from 'react';
import { useTrajectoryStream } from './hooks/useTrajectoryStream';
import { TopBar } from './components/TopBar';
import { IdListPanel } from './components/IdListPanel';
import { TrajectoryCanvas } from './components/TrajectoryCanvas';
import { BlockchainFeed } from './components/BlockchainFeed';

function App() {
  const { 
    positionsById, 
    lastSeenById, 
    blockchainEvents, 
    connectionStatus 
  } = useTrajectoryStream();

  const [selectedId, setSelectedId] = useState<number | null>(null);

  // Derived data
  const activeIds = Array.from(lastSeenById.keys());
  
  // Get current zone for each ID
  const zonesMap = new Map<number, string>();
  positionsById.forEach((points, id) => {
    if (points.length > 0) {
      zonesMap.set(id, points[points.length - 1].zone);
    }
  });

  return (
    <div className="flex flex-col h-screen w-screen bg-hacker-black selection:bg-hacker-red/30 selection:text-white">
      {/* Top Bar */}
      <TopBar 
        connectionStatus={connectionStatus} 
        activeCount={activeIds.length} 
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel: Identity List */}
        <IdListPanel 
          ids={activeIds} 
          selectedId={selectedId} 
          onSelectId={setSelectedId}
          lastSeen={lastSeenById}
          zones={zonesMap}
        />

        {/* Center Canvas: Trajectories */}
        <TrajectoryCanvas 
          positionsById={positionsById} 
          selectedId={selectedId} 
        />

        {/* Right Panel: Event Log */}
        <BlockchainFeed 
          events={blockchainEvents} 
          positions={positionsById} 
        />
      </div>
      
      {/* Footer Info Overlay */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20 pointer-events-none">
        <div className="bg-black/60 backdrop-blur-xl border border-white/5 px-4 py-1 rounded-full flex items-center space-x-4">
          <div className="flex items-center space-x-1">
            <span className="text-[8px] font-black uppercase text-gray-500">System Mode:</span>
            <span className="text-[8px] font-black uppercase text-neon-cyan">{connectionStatus}</span>
          </div>
          <div className="w-px h-2 bg-white/10"></div>
          <div className="flex items-center space-x-1">
            <span className="text-[8px] font-black uppercase text-gray-500">Render Pipeline:</span>
            <span className="text-[8px] font-black uppercase text-white">Canvas2D / HighRes</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
