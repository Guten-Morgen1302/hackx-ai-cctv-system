import React, { useRef, useEffect, useState } from 'react';

const LivenessDetector: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [status, setStatus] = useState<string>("Initializing...");
  const [liveData, setLiveData] = useState<{ bpm: number; snr: number; live: boolean; buffer_percent: number }>({
    bpm: 0,
    snr: 0,
    live: false,
    buffer_percent: 0
  });
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // 1. Setup Camera
    const setupCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, frameRate: 30 } });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        setError("Camera access denied. Please enable webcam.");
      }
    };

    // 2. Setup WebSocket
    const setupWebSocket = () => {
      const ws = new WebSocket("ws://127.0.0.1:8001/ws/liveness");
      ws.onopen = () => setStatus("Connected. Analyzing...");
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setLiveData(data);
        setStatus(data.status);
      };
      ws.onerror = () => setError("WebSocket connection failed.");
      ws.onclose = () => setStatus("Disconnected.");
      wsRef.current = ws;
    };

    setupCamera();
    setupWebSocket();

    return () => {
      wsRef.current?.close();
      if (videoRef.current?.srcObject) {
        (videoRef.current.srcObject as MediaStream).getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  useEffect(() => {
    // Frame capture loop
    const interval = setInterval(() => {
      if (videoRef.current && canvasRef.current && wsRef.current?.readyState === WebSocket.OPEN) {
        const ctx = canvasRef.current.getContext('2d');
        if (ctx) {
          ctx.drawImage(videoRef.current, 0, 0, 160, 120); // Small frame for speed
          const frame = canvasRef.current.toDataURL('image/jpeg', 0.6);
          wsRef.current.send(JSON.stringify({ frame }));
        }
      }
    }, 100); // 10 fps

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col gap-6 p-6 bg-zinc-900 border border-zinc-800 rounded-2xl shadow-xl">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white mb-1">rPPG Liveness Detector</h2>
          <p className="text-zinc-400 text-sm">Heartbeat-based anti-spoofing logic</p>
        </div>
        <div className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider ${
          liveData.live ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 
          status === 'Spoof Detected' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
          'bg-zinc-800 text-zinc-400'
        }`}>
          {status}
        </div>
      </div>

      {error ? (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
          {error}
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="relative aspect-video bg-black rounded-xl overflow-hidden border border-zinc-800">
            <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover grayscale opacity-60" />
            <canvas ref={canvasRef} width="160" height="120" className="hidden" />
            
            {/* Overlay grid */}
            <div className="absolute inset-0 pointer-events-none border-[20px] border-black/20" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-64 border-2 border-white/20 rounded-[40px]" />
          </div>

          <div className="flex flex-col justify-center gap-4">
            <div className="p-4 bg-zinc-800/50 rounded-xl border border-zinc-700">
              <div className="text-zinc-500 text-xs uppercase font-bold mb-1">Estimated Heart Rate</div>
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-mono font-bold text-white">{liveData.bpm > 0 ? liveData.bpm : '--'}</span>
                <span className="text-zinc-400 text-sm">BPM</span>
              </div>
            </div>

            <div className="p-4 bg-zinc-800/50 rounded-xl border border-zinc-700">
              <div className="text-zinc-500 text-xs uppercase font-bold mb-1">Signal Confidence (SNR)</div>
              <div className="flex items-center gap-4">
                <div className="flex-1 h-2 bg-zinc-900 rounded-full overflow-hidden">
                  <div 
                    className={`h-full transition-all duration-500 ${liveData.snr > 2.2 ? 'bg-green-500' : 'bg-red-500'}`}
                    style={{ width: `${Math.min(100, (liveData.snr / 4) * 100)}%` }}
                  />
                </div>
                <span className="text-white font-mono font-bold w-12 text-right">{liveData.snr.toFixed(1)}</span>
              </div>
            </div>

            <div className="p-4 bg-zinc-800/50 rounded-xl border border-zinc-700">
              <div className="text-zinc-500 text-xs uppercase font-bold mb-1">Buffer Stabilization</div>
              <div className="flex items-center gap-4">
                <div className="flex-1 h-2 bg-zinc-900 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-500 transition-all duration-300"
                    style={{ width: `${liveData.buffer_percent}%` }}
                  />
                </div>
                <span className="text-white font-mono font-bold w-12 text-right">{liveData.buffer_percent}%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="text-[10px] text-zinc-500 text-center italic">
        Note: Stay still and ensure good lighting on your forehead for optimal pulse detection.
      </div>
    </div>
  );
};

export default LivenessDetector;
