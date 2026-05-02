import React, { useState, useEffect } from 'react';

interface UPITransactionHoldProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  riskScore: number;
}

const UPITransactionHold: React.FC<UPITransactionHoldProps> = ({ isOpen, onConfirm, onCancel, riskScore }) => {
  const [timeLeft, setTimeLeft] = useState(5);
  const [checklist, setChecklist] = useState({
    notOnCall: false,
    noOneAsked: false,
    verifiedID: false,
  });

  useEffect(() => {
    if (isOpen && timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [isOpen, timeLeft]);

  if (!isOpen) return null;

  const canConfirm = timeLeft === 0 && checklist.notOnCall && checklist.noOneAsked && checklist.verifiedID;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="w-full max-w-md bg-zinc-900 border border-red-500/50 rounded-2xl p-6 shadow-2xl shadow-red-500/20">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-red-500/20 rounded-full">
            <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-white">High Risk Transaction Detect</h2>
        </div>

        <p className="text-zinc-400 mb-6">
          Security systems have detected a high risk score of <span className="text-red-500 font-mono font-bold">{riskScore}/100</span>. 
          Please complete the mandatory cooling-off period and safety checklist.
        </p>

        <div className="space-y-4 mb-8">
          <label className="flex items-center gap-3 cursor-pointer group">
            <input 
              type="checkbox" 
              checked={checklist.notOnCall}
              onChange={(e) => setChecklist({ ...checklist, notOnCall: e.target.checked })}
              className="w-5 h-5 rounded border-zinc-700 bg-zinc-800 text-red-500 focus:ring-red-500"
            />
            <span className="text-zinc-300 group-hover:text-white transition-colors">I am NOT currently on a call with anyone</span>
          </label>
          <label className="flex items-center gap-3 cursor-pointer group">
            <input 
              type="checkbox" 
              checked={checklist.noOneAsked}
              onChange={(e) => setChecklist({ ...checklist, noOneAsked: e.target.checked })}
              className="w-5 h-5 rounded border-zinc-700 bg-zinc-800 text-red-500 focus:ring-red-500"
            />
            <span className="text-zinc-300 group-hover:text-white transition-colors">No one asked me to make this payment to "receive" money</span>
          </label>
          <label className="flex items-center gap-3 cursor-pointer group">
            <input 
              type="checkbox" 
              checked={checklist.verifiedID}
              onChange={(e) => setChecklist({ ...checklist, verifiedID: e.target.checked })}
              className="w-5 h-5 rounded border-zinc-700 bg-zinc-800 text-red-500 focus:ring-red-500"
            />
            <span className="text-zinc-300 group-hover:text-white transition-colors">I have independently verified the recipient's identity</span>
          </label>
        </div>

        <div className="flex gap-4">
          <button 
            onClick={onCancel}
            className="flex-1 px-4 py-3 bg-zinc-800 hover:bg-zinc-700 text-white font-medium rounded-xl transition-all"
          >
            Cancel Payment
          </button>
          <button 
            disabled={!canConfirm}
            onClick={onConfirm}
            className={`flex-1 px-4 py-3 font-bold rounded-xl transition-all ${
              canConfirm 
                ? 'bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-600/20' 
                : 'bg-zinc-800 text-zinc-500 cursor-not-allowed'
            }`}
          >
            {timeLeft > 0 ? `Wait ${timeLeft}s` : 'Confirm Payment'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UPITransactionHold;
