import React, { useRef, useEffect } from 'react';
import type { PositionPoint } from '../types';

interface TrajectoryCanvasProps {
  positionsById: Map<number, PositionPoint[]>;
  selectedId: number | null;
}

export const TrajectoryCanvas: React.FC<TrajectoryCanvasProps> = ({ positionsById, selectedId }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationId: number;

    const render = () => {
      const width = canvas.width;
      const height = canvas.height;

      // Clear with dark gradient feel
      ctx.fillStyle = '#050509';
      ctx.fillRect(0, 0, width, height);

      // Draw Grid
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
      ctx.lineWidth = 1;
      const gridSize = 40;
      for (let x = 0; x <= width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y <= height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // --- SECURITY ZONES CONFIG ---
      const zones = [
        { name: 'ENTRY LOBBY', x: 0.05, y: 0.05, w: 0.28, h: 0.4, color: '#00f6ff' },
        { name: 'CORRIDOR A', x: 0.35, y: 0.05, w: 0.3, h: 0.25, color: '#39ff14' },
        { name: 'ZONE B', x: 0.68, y: 0.05, w: 0.27, h: 0.25, color: '#3b82f6' },
        { name: 'PARKING ENTRY', x: 0.05, y: 0.5, w: 0.28, h: 0.45, color: '#a855f7' },
        { name: 'MAIN HALL', x: 0.35, y: 0.35, w: 0.3, h: 0.3, color: '#64748b' },
        { name: 'EXIT GATE', x: 0.68, y: 0.35, w: 0.27, h: 0.3, color: '#f59e0b' },
        { name: 'RESTRICTED AREA', x: 0.35, y: 0.7, w: 0.6, h: 0.25, color: '#ff2040' },
      ];

      zones.forEach(z => {
        const zx = z.x * width;
        const zy = z.y * height;
        const zw = z.w * width;
        const zh = z.h * height;

        // Zone Fill (very faint)
        ctx.fillStyle = `${z.color}08`; // 08 hex alpha
        ctx.fillRect(zx, zy, zw, zh);

        // Zone Outline
        ctx.strokeStyle = `${z.color}22`;
        ctx.setLineDash([5, 5]);
        ctx.strokeRect(zx, zy, zw, zh);
        ctx.setLineDash([]);

        // Zone Label
        ctx.fillStyle = `${z.color}aa`;
        ctx.font = 'black 9px JetBrains Mono';
        ctx.fillText(z.name, zx + 5, zy + 12);
      });
      // -----------------------------

      // Draw Trajectories
      positionsById.forEach((points, id) => {
        if (points.length < 2) return;

        const isSelected = selectedId === id;
        const isDimmed = selectedId !== null && !isSelected;

        // Path Color
        if (isSelected) {
          ctx.strokeStyle = '#39ff14'; // Neon Green
          ctx.lineWidth = 3;
          ctx.shadowBlur = 15;
          ctx.shadowColor = '#39ff14';
        } else if (isDimmed) {
          ctx.strokeStyle = 'rgba(255, 32, 64, 0.1)'; // Very faint red
          ctx.lineWidth = 1;
          ctx.shadowBlur = 0;
        } else {
          ctx.strokeStyle = 'rgba(0, 246, 255, 0.4)'; // Cyan
          ctx.lineWidth = 1.5;
          ctx.shadowBlur = 5;
          ctx.shadowColor = 'rgba(0, 246, 255, 0.5)';
        }

        ctx.beginPath();
        points.forEach((p, i) => {
          const x = p.x * width;
          const y = p.y * height;
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        });
        ctx.stroke();

        // Draw Current Position Dot
        const last = points[points.length - 1];
        ctx.fillStyle = isSelected ? '#39ff14' : isDimmed ? 'rgba(255, 32, 64, 0.2)' : '#00f6ff';
        ctx.shadowBlur = isSelected ? 20 : 5;
        ctx.beginPath();
        ctx.arc(last.x * width, last.y * height, isSelected ? 6 : 4, 0, Math.PI * 2);
        ctx.fill();

        // Label
        if (isSelected || !isDimmed) {
          ctx.fillStyle = '#fff';
          ctx.font = 'bold 10px JetBrains Mono';
          ctx.shadowBlur = 0;
          ctx.fillText(`ID:${id}`, last.x * width + 8, last.y * height - 8);
        }
      });

      animationId = requestAnimationFrame(render);
    };

    // Resize handler
    const resize = () => {
      if (canvas.parentElement) {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
      }
    };
    window.addEventListener('resize', resize);
    resize();

    render();

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', resize);
    };
  }, [positionsById, selectedId]);

  return (
    <div className="flex-1 h-full relative overflow-hidden bg-hacker-black">
      <div className="absolute top-4 left-6 z-10 pointer-events-none">
        <h2 className="text-[10px] font-black uppercase tracking-[0.3em] text-white/40">
          Trajectory Map <span className="mx-2 opacity-50">•</span> Focus: {selectedId ? `ID ${selectedId}` : 'ALL'}
        </h2>
      </div>
      
      <canvas ref={canvasRef} className="w-full h-full block" />
      
      <div className="absolute bottom-4 left-6 z-10 flex items-center space-x-6">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-[2px] bg-neon-green shadow-[0_0_5px_#39ff14]"></div>
          <span className="text-[9px] font-bold text-gray-500 uppercase tracking-widest">Selected ID path</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-[2px] bg-hacker-red opacity-30"></div>
          <span className="text-[9px] font-bold text-gray-400/30 uppercase tracking-widest">Other tracks</span>
        </div>
      </div>

      <div className="absolute bottom-4 right-6 z-10">
        <span className="text-[9px] font-bold text-white/20 uppercase tracking-widest">Coord Sys: Normalized [0,1]</span>
      </div>
    </div>
  );
};
