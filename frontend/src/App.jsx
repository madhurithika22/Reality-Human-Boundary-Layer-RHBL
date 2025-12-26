import React, { useState, useEffect, useRef } from 'react';
import { ShieldCheck, Upload, RefreshCw, CheckCircle, Circle, Play, Activity, Smile, Eye } from 'lucide-react';

function App() {
  const [data, setData] = useState({ 
    score: 0.0, 
    quality: 0.0,
    prompt: "Loading...", 
    rppg_wave: [], 
    checks: {} 
  });
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    const interval = setInterval(() => {
      fetch('http://127.0.0.1:8000/stats')
        .then(res => res.json())
        .then(setData)
        .catch(console.error);
    }, 100);
    return () => clearInterval(interval);
  }, []);

  const handleUpload = async (e) => {
    if (!e.target.files[0]) return;
    setIsUploading(true);
    const fd = new FormData();
    fd.append("file", e.target.files[0]);
    await fetch('http://127.0.0.1:8000/upload_video', { method: 'POST', body: fd });
    setIsUploading(false);
  };

  const handleReset = () => fetch('http://127.0.0.1:8000/reset_camera', { method: 'POST' });

  // Convert float 0.0-1.0 to Percentage 0-100 for display
  const displayScore = Math.round(data.score * 100);
  const displayQuality = Math.round((data.quality || 0) * 100);

  return (
    <div className="h-screen w-screen bg-gray-50 text-slate-800 font-sans p-4 flex flex-col overflow-hidden">
      
      {/* Header */}
      <div className="flex items-center gap-4 mb-4 shrink-0 bg-white p-3 rounded-2xl shadow-sm border border-gray-200">
        <div className="w-10 h-10 bg-[#1e293b] rounded flex items-center justify-center shadow-lg shadow-blue-500/10">
          <ShieldCheck className="text-white" size={24} />
        </div>
        <div>
            <h1 className="text-2xl font-bold tracking-widest text-[#1e293b]">HUMAN <span className="text-[#06b6d4]">AUTHENTICITY</span></h1>
            <p className="text-[10px] text-slate-400 font-bold tracking-[0.2em] uppercase">RHBL • Layer A • Biometric Engine</p>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-12 gap-4 min-h-0">
        
        {/* LEFT: Video & Controls */}
        <div className="col-span-8 flex flex-col gap-4 min-h-0">
          <div className="flex-1 bg-white rounded-2xl border border-gray-200 relative overflow-hidden flex flex-col shadow-lg">
            <div className="absolute top-4 left-4 z-20 bg-[#1e293b]/90 px-3 py-1.5 rounded text-xs font-mono text-white border border-blue-500/30 shadow-sm flex items-center gap-2">
              <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span> LIVE SEQUENCE
            </div>
            
            <div className="flex-1 relative flex items-center justify-center bg-gray-100">
               <img src="http://127.0.0.1:8000/video_feed" className="max-w-full max-h-full object-contain" />
               {displayScore >= 98 && (
                 <div className="absolute inset-0 bg-[#1e293b]/60 backdrop-blur-sm flex flex-col items-center justify-center animate-in fade-in">
                   <CheckCircle size={80} className="text-[#06b6d4] mb-2 drop-shadow-[0_0_15px_rgba(6,182,212,0.6)]" />
                   <h2 className="text-3xl font-black text-white tracking-widest">VERIFIED</h2>
                   <p className="text-cyan-200 font-mono mt-2">Score: {data.score}</p>
                 </div>
               )}
            </div>

            <div className="h-14 bg-[#1e293b] border-t border-gray-200 flex items-center justify-center shrink-0">
              <p className="font-mono text-xl font-bold text-white tracking-wider animate-pulse">{data.prompt}</p>
            </div>
          </div>

          <div className="h-16 bg-white rounded-xl border border-gray-200 flex items-center px-6 gap-4 shrink-0 shadow-sm">
             <input type="file" ref={fileInputRef} onChange={handleUpload} className="hidden" accept="video/*" />
             <button onClick={() => fileInputRef.current.click()} className="flex items-center gap-2 px-6 py-2 bg-[#1e293b] hover:bg-blue-900 text-white rounded-lg font-bold transition-all shadow-md shadow-slate-300">
               {isUploading ? "Uploading..." : <><Upload size={20} /> Upload Video</>}
             </button>
             <button onClick={handleReset} className="flex items-center gap-2 px-6 py-2 bg-gray-100 hover:bg-gray-200 text-slate-700 rounded-lg font-bold transition-all border border-gray-300">
               <RefreshCw size={20} /> Reset Camera
             </button>
          </div>
        </div>

        {/* RIGHT: Data Panel */}
        <div className="col-span-4 flex flex-col gap-4 min-h-0">
          
          {/* Score */}
          <div className="bg-white p-6 rounded-2xl border border-gray-200 text-center shrink-0 shadow-sm">
            <p className="text-xs font-bold text-[#64748b] uppercase tracking-widest mb-1">Authenticity Score (0-1.0)</p>
            <p className={`text-6xl font-black ${displayScore >= 98 ? 'text-[#06b6d4]' : 'text-[#1e293b]'}`}>{data.score}</p>
            <p className="text-xs text-slate-400 mt-2 font-mono">Quality Index: {data.quality}</p>
          </div>

          {/* rPPG Graph */}
          <div className="bg-white p-4 rounded-2xl border border-gray-200 h-32 shrink-0 flex flex-col shadow-sm">
            <div className="flex items-center gap-2 mb-2 text-xs font-bold text-[#64748b] uppercase tracking-widest">
               <Activity size={14} className="text-[#06b6d4]" /> Bio-Signal
            </div>
            <div className="flex-1 bg-gray-50 rounded border border-gray-200 flex items-end px-1 pb-1 gap-[1px]">
               {data.rppg_wave && data.rppg_wave.map((v, i) => (
                 <div key={i} className="w-full bg-[#06b6d4]" style={{height: `${v*100}%`}}></div>
               ))}
            </div>
          </div>

          {/* Checklist */}
          <div className="flex-1 bg-white p-4 rounded-2xl border border-gray-200 flex flex-col gap-2 overflow-y-auto shadow-sm">
             <p className="text-xs font-bold text-[#64748b] uppercase tracking-widest border-b border-gray-200 pb-2 mb-1">Verification Steps</p>
             <CheckItem label="1. Calibration" done={data.checks?.calibrated} icon={<Play size={16}/>} />
             <CheckItem label="2. Head Turn (Hold 0.5s)" done={data.checks?.turned} icon={<RefreshCw size={16}/>} />
             <CheckItem label="3. Smile Check (Hold 1.0s)" done={data.checks?.smiled} icon={<Smile size={16}/>} />
             <CheckItem label="4. Eye Blink" done={data.checks?.blinked} icon={<Eye size={16}/>} />
          </div>
        </div>
      </div>
    </div>
  );
}

const CheckItem = ({ label, done, icon }) => (
  <div className={`flex items-center justify-between p-3 rounded-xl border ${done ? 'bg-blue-50 border-blue-200 text-blue-900' : 'bg-gray-50 border-gray-200 text-slate-500'}`}>
     <div className="flex items-center gap-3">
       <div className={done ? 'text-[#06b6d4]' : 'text-slate-400'}>{icon}</div>
       <span className="font-medium text-sm">{label}</span>
     </div>
     {done ? <CheckCircle size={18} className="text-[#06b6d4]" /> : <Circle size={18} />}
  </div>
);

export default App;