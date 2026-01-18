import React, { useState, useEffect } from 'react';
import { ShieldCheck, Activity, Brain, AlertTriangle, Play, Square } from 'lucide-react';

function App() {
  // New: isPaused state to control polling
  const [isPaused, setIsPaused] = useState(false);
  
  const [stats, setStats] = useState({
    trust_score: 0,
    layer_scores: { 
      human_authenticity: 0, 
      reality_consistency: 0,
      manipulation_risk: 0 
    },
    violated_rules: [],
    prompt: "INITIALIZING...",
    rppg_wave: []
  });

  useEffect(() => {
    let interval;
    // Only poll the backend if the system is NOT paused
    if (!isPaused) {
      interval = setInterval(async () => {
        try {
          const res = await fetch('http://localhost:8000/stats');
          const data = await res.json();
          // Update state with new data
          setStats(prev => ({ ...prev, ...data }));
        } catch (e) { 
          console.error("Stats error", e); 
        }
      }, 200);
    }
    return () => clearInterval(interval);
  }, [isPaused]); // Depend on isPaused

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8 font-sans">
      <header className="flex justify-between items-center mb-8 border-b border-slate-700 pb-4">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <ShieldCheck className="text-cyan-400" /> RHBL Infrastructure
        </h1>
        
        {/* Added: Control Button Section */}
        <div className="flex items-center gap-4">
          <button 
            onClick={() => setIsPaused(!isPaused)}
            className={`flex items-center gap-2 px-6 py-2 rounded-lg font-bold transition-all shadow-lg ${
              isPaused 
                ? 'bg-green-600 hover:bg-green-500 ring-2 ring-green-400' 
                : 'bg-red-600 hover:bg-red-500 ring-2 ring-red-400'
            }`}
          >
            {isPaused ? <><Play size={18}/> RESUME SCAN</> : <><Square size={18}/> STOP & ANALYZE</>}
          </button>
          <div className="px-4 py-1 bg-slate-800 rounded-full text-sm font-mono border border-slate-600">
            SYSTEM: <span className={isPaused ? "text-yellow-400" : "text-green-400"}>
              {isPaused ? "ANALYSIS MODE" : "ACTIVE"}
            </span>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Video Feed Section */}
        <div className="lg:col-span-2 space-y-4">
          <div className="relative rounded-2xl overflow-hidden border-4 border-slate-800 bg-black aspect-video shadow-2xl">
            {/* Display static message if paused, otherwise show feed */}
            {!isPaused ? (
              <img src="http://localhost:8000/video_feed" className="w-full h-full object-cover" alt="Live Feed" />
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-slate-800 text-slate-400 italic">
                Video Feed Frozen for Signal Analysis
              </div>
            )}
            <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-md px-4 py-2 rounded-lg border border-white/20">
              <p className="text-cyan-400 font-bold animate-pulse">{stats.prompt}</p>
            </div>
          </div>
          
          {/* Physiological Waveform (rPPG) */}
          <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
            <h3 className="text-xs uppercase tracking-widest text-slate-400 mb-2 flex items-center gap-2">
              <Activity size={14} /> Biological Pulse Signal (rPPG)
            </h3>
            <div className="h-20 flex items-end gap-1 overflow-hidden">
              {stats.rppg_wave && stats.rppg_wave.length > 0 ? (
                stats.rppg_wave.slice(-100).map((val, i) => (
                  <div key={i} className="bg-cyan-500 w-1 min-w-[2px] rounded-t transition-all" style={{ height: `${val * 100}%` }} />
                ))
              ) : (
                <div className="text-slate-600 italic text-sm w-full text-center pb-4">Extracting heart rate signals...</div>
              )}
            </div>
          </div>
        </div>

        {/* Intelligence & Trust Layer Section */}
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 p-6 rounded-2xl border border-slate-700 shadow-xl">
            <h2 className="text-slate-400 text-sm font-semibold uppercase mb-4">Final Trust Judgment</h2>
            <div className="text-6xl font-black text-white mb-2">{stats.trust_score}%</div>
            <div className="w-full bg-slate-700 h-3 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all duration-700 ${stats.trust_score > 80 ? 'bg-green-500' : 'bg-red-500'}`}
                style={{ width: `${stats.trust_score}%` }}
              />
            </div>
          </div>

          <div className="space-y-4">
            {/* Authenticity Layer */}
            <div className="bg-slate-800 p-4 rounded-xl border border-slate-700">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-slate-400">Human Authenticity</span>
                <span className="text-cyan-400 font-bold">{stats.layer_scores.human_authenticity}%</span>
              </div>
              <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
                <div className="bg-cyan-500 h-full" style={{ width: `${stats.layer_scores.human_authenticity}%` }} />
              </div>
            </div>
            
            {/* Reality Layer */}
            <div className="bg-slate-800 p-4 rounded-xl border border-slate-700">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-slate-400">Reality Consistency</span>
                <span className="text-purple-400 font-bold">{stats.layer_scores.reality_consistency}%</span>
              </div>
              <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
                <div className="bg-purple-500 h-full" style={{ width: `${stats.layer_scores.reality_consistency}%` }} />
              </div>
            </div>

            {/* Manipulation Layer */}
            <div className="bg-slate-800 p-4 rounded-xl border border-slate-700">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-slate-400">Manipulation Risk</span>
                <span className="text-red-400 font-bold">{stats.layer_scores.manipulation_risk}%</span>
              </div>
              <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
                <div className="bg-red-500 h-full transition-all" style={{ width: `${stats.layer_scores.manipulation_risk}%` }} />
              </div>
            </div>
          </div>

          <div className="bg-slate-800/80 p-6 rounded-2xl border border-slate-700 min-h-[200px]">
            <h3 className="text-slate-400 text-xs font-bold uppercase mb-4 flex items-center gap-2"><Brain size={16} /> Reasoning Trace</h3>
            <div className="space-y-3">
              {stats.violated_rules.length > 0 ? (
                stats.violated_rules.map((rule, i) => (
                  <div key={i} className="flex gap-3 text-sm text-red-400 bg-red-400/10 p-2 rounded-lg border border-red-400/20">
                    <AlertTriangle size={18} className="shrink-0" />
                    <span>{rule}</span>
                  </div>
                ))
              ) : (
                <div className="text-slate-500 text-sm italic text-center pt-8">Scanning consistency layers...</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;