import { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
import { ArrowRight, Terminal, RefreshCw, Zap, Upload, LayoutDashboard, ShieldCheck, Activity, Code2, Database, ListTree, Package, Route } from 'lucide-react';

function App() {
  const [cobolCode, setCobolCode] = useState(`IDENTIFICATION DIVISION.
PROGRAM-ID. HELLO-WORLD.

PROCEDURE DIVISION.
    DISPLAY "Hello world!".
    STOP RUN.`);
  
  const [jclCode, setJclCode] = useState(`//JOB1     JOB (ACCT),'BATCH JOB',CLASS=A,MSGCLASS=X
//STEP1    EXEC PGM=IEFBR14
//DD1      DD DSN=USER.DATA,DISP=(NEW,CATLG,DELETE)`);
    
  const [pythonCode, setPythonCode] = useState('');
  const [airflowCode, setAirflowCode] = useState('');
  
  const [isTranslating, setIsTranslating] = useState(false);
  const [isTranslatingJcl, setIsTranslatingJcl] = useState(false);
  
  const [activeTab, setActiveTab] = useState('editor'); // editor, roi, logs, security, dependencies, traceability, jcl
  
  const [metrics, setMetrics] = useState({ linesProcessed: 0, mipsSaved: 0, cloudCostMonthly: 0 });
  const [logs, setLogs] = useState<string[]>([]);
  const [securityPatches, setSecurityPatches] = useState<string[]>([]);
  const [dependencies, setDependencies] = useState<string[]>([]);
  const [traceability, setTraceability] = useState<{cobol: string, python: string}[]>([]);

  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logsEndRef.current) {
        logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, activeTab]);

  const handleTranslate = async () => {
    if (!cobolCode.trim()) return;
    setIsTranslating(true);
    setActiveTab('logs');
    setPythonCode('');
    setLogs(['[SYSTEM] Initializing connection to Translation Engine...', '[SYSTEM] Analyzing AST structure...']);
    setSecurityPatches([]);
    setDependencies([]);
    setTraceability([]);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/translate_live', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: cobolCode })
      });

      if (!response.ok) throw new Error("API Connection Failed");

      const data = await response.json();
      
      let logIndex = 0;
      const streamLogs = () => {
        if (logIndex < data.logs.length) {
            setLogs(prev => [...prev, data.logs[logIndex]]);
            logIndex++;
            setTimeout(streamLogs, 300);
        } else {
            setMetrics(data.metrics || { linesProcessed: 0, mipsSaved: 0, cloudCostMonthly: 0 });
            setSecurityPatches(data.security || []);
            setDependencies(data.dependencies || []);
            setTraceability(data.traceability || []);
            
            let i = 0;
            const typeChar = () => {
              if (i < data.code.length) {
                setPythonCode(prev => prev + data.code.charAt(i));
                i++;
                setTimeout(typeChar, Math.random() * 2 + 1);
              } else {
                setIsTranslating(false);
                setActiveTab('editor');
              }
            };
            typeChar();
        }
      }
      streamLogs();

    } catch (err) {
      console.error(err);
      setLogs(prev => [...prev, '[ERROR] Connection to backend failed.']);
      setPythonCode('# Error connecting to backend.');
      setIsTranslating(false);
    }
  };

  const handleJclTranslate = async () => {
    if (!jclCode.trim()) return;
    setIsTranslatingJcl(true);
    setAirflowCode('// Generating Airflow DAG...');
    
    try {
      const response = await fetch('http://127.0.0.1:8000/api/translate_jcl', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: jclCode })
      });
      const data = await response.json();
      setAirflowCode('');
      
      let i = 0;
      const typeChar = () => {
        if (i < data.code.length) {
          setAirflowCode(prev => prev + data.code.charAt(i));
          i++;
          setTimeout(typeChar, 2);
        } else {
          setIsTranslatingJcl(false);
        }
      };
      typeChar();
    } catch (err) {
      setAirflowCode('# Error connecting to backend.');
      setIsTranslatingJcl(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#EDEDED] flex flex-col font-sans selection:bg-cyan-500/30">
      <header className="border-b border-[#333] bg-[#000] px-6 py-4 flex justify-between items-center sticky top-0 z-20 shadow-md">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-md bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Terminal className="text-white w-5 h-5" />
          </div>
          <h1 className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">QuantumForge AI Pipeline</h1>
        </div>
        
        {/* Navigation Tabs */}
        <div className="flex flex-wrap items-center justify-center gap-1 bg-[#111] p-1 rounded-lg border border-[#333]">
            <button onClick={() => setActiveTab('editor')} className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${activeTab === 'editor' ? 'bg-[#222] text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'}`}>
                <Code2 className="w-4 h-4" /> Code
            </button>
            <button onClick={() => setActiveTab('jcl')} className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${activeTab === 'jcl' ? 'bg-[#222] text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'}`}>
                <Route className="w-4 h-4" /> JCL Orchestration
            </button>
            <button onClick={() => setActiveTab('roi')} className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${activeTab === 'roi' ? 'bg-[#222] text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'}`}>
                <LayoutDashboard className="w-4 h-4" /> ROI
            </button>
            <button onClick={() => setActiveTab('logs')} className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${activeTab === 'logs' ? 'bg-[#222] text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'}`}>
                <Activity className="w-4 h-4" /> CI/CD Logs
            </button>
            <button onClick={() => setActiveTab('security')} className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${activeTab === 'security' ? 'bg-[#222] text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'}`}>
                <ShieldCheck className="w-4 h-4" /> Security
            </button>
            <button onClick={() => setActiveTab('traceability')} className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${activeTab === 'traceability' ? 'bg-[#222] text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'}`}>
                <ListTree className="w-4 h-4" /> Traceability
            </button>
            <button onClick={() => setActiveTab('dependencies')} className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${activeTab === 'dependencies' ? 'bg-[#222] text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'}`}>
                <Package className="w-4 h-4" /> Dependencies
            </button>
        </div>

        <div className="flex items-center gap-4 text-sm">
          <button 
            onClick={activeTab === 'jcl' ? handleJclTranslate : handleTranslate}
            disabled={isTranslating || isTranslatingJcl}
            className={`flex items-center gap-2 px-5 py-2 rounded-md font-semibold transition-all shadow-lg ${isTranslating || isTranslatingJcl ? 'bg-[#222] text-gray-500 cursor-not-allowed border border-[#333]' : 'bg-white text-black hover:bg-gray-100 hover:scale-105 active:scale-95'}`}
          >
            {(isTranslating || isTranslatingJcl) ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4 text-black" />}
            {(isTranslating || isTranslatingJcl) ? 'Processing...' : 'Run Pipeline'}
          </button>
        </div>
      </header>

      <main className="flex-1 flex overflow-hidden relative bg-[#0A0A0A]">
        {/* Tab Content: Editor */}
        {activeTab === 'editor' && (
            <div className="flex-1 flex overflow-hidden w-full animate-in fade-in duration-300">
                <section className="flex-1 flex flex-col border-r border-[#333] relative bg-[#111]">
                <div className="border-b border-[#333] px-4 py-3 flex justify-between items-center text-xs uppercase tracking-widest text-gray-400 font-bold bg-[#0A0A0A]">
                    <span className="flex items-center gap-2"><Database className="w-4 h-4"/> Legacy System (COBOL/DB2)</span>
                    <span title="Drag & Drop Supported"><Upload className="w-4 h-4 cursor-pointer hover:text-white transition-colors" /></span>
                </div>
                <div className="flex-1 relative">
                    <Editor
                    height="100%"
                    defaultLanguage="cobol"
                    theme="vs-dark"
                    value={cobolCode}
                    onChange={(val) => setCobolCode(val || '')}
                    options={{ minimap: { enabled: false }, fontSize: 14, fontFamily: "'JetBrains Mono', monospace", padding: { top: 20 } }}
                    />
                </div>
                </section>
                <div className="w-16 bg-[#0A0A0A] border-r border-[#333] flex flex-col items-center justify-center relative z-10">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center border transition-all ${isTranslating ? 'bg-cyan-500/10 border-cyan-500/50 animate-pulse shadow-[0_0_15px_rgba(6,182,212,0.5)]' : 'bg-[#111] border-[#333]'}`}>
                        <ArrowRight className={`w-5 h-5 ${isTranslating ? 'text-cyan-400' : 'text-gray-500'}`} />
                    </div>
                </div>
                <section className="flex-1 flex flex-col relative bg-[#111]">
                <div className="border-b border-[#333] px-4 py-3 flex justify-between items-center text-xs uppercase tracking-widest text-gray-400 font-bold bg-[#0A0A0A]">
                    <span className="flex items-center gap-2"><Code2 className="w-4 h-4"/> Modern Cloud (Python/SQLAlchemy)</span>
                </div>
                <div className="flex-1 relative">
                    <Editor
                    height="100%"
                    defaultLanguage="python"
                    theme="vs-dark"
                    value={pythonCode}
                    options={{ readOnly: true, minimap: { enabled: false }, fontSize: 14, fontFamily: "'JetBrains Mono', monospace", padding: { top: 20 } }}
                    />
                </div>
                </section>
            </div>
        )}

        {/* Tab Content: JCL Orchestration */}
        {activeTab === 'jcl' && (
            <div className="flex-1 flex overflow-hidden w-full animate-in fade-in duration-300">
                <section className="flex-1 flex flex-col border-r border-[#333] relative bg-[#111]">
                <div className="border-b border-[#333] px-4 py-3 flex justify-between items-center text-xs uppercase tracking-widest text-gray-400 font-bold bg-[#0A0A0A]">
                    <span className="flex items-center gap-2"><Terminal className="w-4 h-4"/> Legacy IBM JCL</span>
                </div>
                <div className="flex-1 relative">
                    <Editor
                    height="100%"
                    defaultLanguage="shell"
                    theme="vs-dark"
                    value={jclCode}
                    onChange={(val) => setJclCode(val || '')}
                    options={{ minimap: { enabled: false }, fontSize: 14, fontFamily: "'JetBrains Mono', monospace", padding: { top: 20 } }}
                    />
                </div>
                </section>
                <div className="w-16 bg-[#0A0A0A] border-r border-[#333] flex flex-col items-center justify-center relative z-10">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center border transition-all ${isTranslatingJcl ? 'bg-purple-500/10 border-purple-500/50 animate-pulse shadow-[0_0_15px_rgba(168,85,247,0.5)]' : 'bg-[#111] border-[#333]'}`}>
                        <ArrowRight className={`w-5 h-5 ${isTranslatingJcl ? 'text-purple-400' : 'text-gray-500'}`} />
                    </div>
                </div>
                <section className="flex-1 flex flex-col relative bg-[#111]">
                <div className="border-b border-[#333] px-4 py-3 flex justify-between items-center text-xs uppercase tracking-widest text-gray-400 font-bold bg-[#0A0A0A]">
                    <span className="flex items-center gap-2"><Route className="w-4 h-4"/> Apache Airflow DAG</span>
                </div>
                <div className="flex-1 relative">
                    <Editor
                    height="100%"
                    defaultLanguage="python"
                    theme="vs-dark"
                    value={airflowCode}
                    options={{ readOnly: true, minimap: { enabled: false }, fontSize: 14, fontFamily: "'JetBrains Mono', monospace", padding: { top: 20 } }}
                    />
                </div>
                </section>
            </div>
        )}

        {/* Tab Content: ROI Dashboard */}
        {activeTab === 'roi' && (
            <div className="flex-1 p-8 overflow-y-auto animate-in fade-in duration-300 flex flex-col items-center">
                <div className="max-w-4xl w-full">
                    <h2 className="text-3xl font-bold mb-8 flex items-center gap-3"><LayoutDashboard className="text-cyan-400"/> Executive ROI Dashboard</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                        <div className="bg-[#111] border border-[#333] rounded-xl p-6 flex flex-col justify-center items-center shadow-lg hover:border-gray-500 transition-colors">
                            <span className="text-gray-400 text-sm font-semibold uppercase tracking-wider mb-2">Lines Processed</span>
                            <span className="text-5xl font-black text-white">{metrics.linesProcessed}</span>
                        </div>
                        <div className="bg-[#111] border border-cyan-500/30 rounded-xl p-6 flex flex-col justify-center items-center shadow-[0_0_20px_rgba(6,182,212,0.1)] hover:border-cyan-400 transition-colors">
                            <span className="text-cyan-400 text-sm font-semibold uppercase tracking-wider mb-2">Mainframe MIPS Saved</span>
                            <span className="text-5xl font-black text-white">{metrics.mipsSaved}</span>
                        </div>
                        <div className="bg-[#111] border border-[#333] rounded-xl p-6 flex flex-col justify-center items-center shadow-lg hover:border-gray-500 transition-colors">
                            <span className="text-gray-400 text-sm font-semibold uppercase tracking-wider mb-2">Est. Cloud Cost ($/mo)</span>
                            <span className="text-5xl font-black text-green-400">${metrics.cloudCostMonthly}</span>
                        </div>
                    </div>
                </div>
            </div>
        )}

        {/* Tab Content: Traceability Matrix */}
        {activeTab === 'traceability' && (
            <div className="flex-1 p-8 overflow-y-auto animate-in fade-in duration-300 flex justify-center">
                <div className="max-w-4xl w-full">
                    <h2 className="text-3xl font-bold mb-4 flex items-center gap-3"><ListTree className="text-blue-400"/> Audit Traceability Matrix</h2>
                    <p className="text-gray-400 mb-8">Line-by-line mapping for strict financial regulatory compliance.</p>
                    
                    {traceability.length === 0 ? (
                        <div className="bg-[#111] border border-[#333] rounded-xl p-12 text-center text-gray-500">Run the pipeline first to generate audit trace.</div>
                    ) : (
                        <div className="bg-[#111] border border-[#333] rounded-xl overflow-hidden shadow-lg">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="bg-[#1a1a1a] border-b border-[#333]">
                                        <th className="p-4 font-semibold text-gray-300 w-1/2">Legacy COBOL Origin</th>
                                        <th className="p-4 font-semibold text-gray-300 w-1/2">Modern Python Implementation</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {traceability.map((item, i) => (
                                        <tr key={i} className="border-b border-[#222] hover:bg-[#151515]">
                                            <td className="p-4 font-mono text-sm text-gray-400">{item.cobol}</td>
                                            <td className="p-4 font-mono text-sm text-cyan-400">{item.python}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        )}

        {/* Tab Content: Dependencies */}
        {activeTab === 'dependencies' && (
            <div className="flex-1 p-8 overflow-y-auto animate-in fade-in duration-300 flex justify-center">
                <div className="max-w-4xl w-full">
                    <h2 className="text-3xl font-bold mb-4 flex items-center gap-3"><Package className="text-orange-400"/> Automated Dependencies</h2>
                    <p className="text-gray-400 mb-8">Dynamically resolved requirements_supplemental.txt based on AST code intelligence.</p>
                    {dependencies.length === 0 ? (
                        <div className="bg-[#111] border border-[#333] rounded-xl p-12 text-center text-gray-500">Run the pipeline first to resolve pip dependencies.</div>
                    ) : (
                        <div className="bg-[#050505] border border-[#333] rounded-xl p-6 font-mono text-sm shadow-inner overflow-y-auto space-y-2">
                            {dependencies.map((dep, i) => (
                                <div key={i} className="text-orange-300">{dep}</div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        )}

        {/* Tab Content: CI/CD Logs (Self-Healing) */}
        {activeTab === 'logs' && (
            <div className="flex-1 p-8 overflow-y-auto animate-in fade-in duration-300">
                <div className="max-w-4xl mx-auto h-full flex flex-col">
                    <h2 className="text-3xl font-bold mb-4 flex items-center gap-3"><Activity className="text-yellow-400"/> Autonomous Self-Healing Pipeline</h2>
                    <div className="flex-1 bg-[#050505] border border-[#333] rounded-xl p-6 font-mono text-sm shadow-inner overflow-y-auto">
                        {logs.length === 0 ? (
                            <div className="text-gray-600 italic">No pipeline executions yet.</div>
                        ) : (
                            <div className="space-y-3">
                                {logs.map((log, i) => (
                                    <div key={i} className={`pb-2 border-b border-[#111] ${log.includes('[ERROR]') || log.includes('[WARN]') ? 'text-red-400' : log.includes('SUCCESS') || log.includes('passed') ? 'text-green-400' : 'text-gray-300'}`}>
                                        <span className="opacity-50 mr-3">{new Date().toISOString().split('T')[1].substring(0,8)}</span>
                                        {log}
                                    </div>
                                ))}
                                {isTranslating && <div className="text-cyan-400 mt-4"><RefreshCw className="w-4 h-4 animate-spin inline-block mr-2" /> Thinking...</div>}
                                <div ref={logsEndRef} />
                            </div>
                        )}
                    </div>
                </div>
            </div>
        )}

        {/* Tab Content: Security Audit */}
        {activeTab === 'security' && (
            <div className="flex-1 p-8 overflow-y-auto animate-in fade-in duration-300 flex justify-center">
                <div className="max-w-4xl w-full">
                    <h2 className="text-3xl font-bold mb-4 flex items-center gap-3"><ShieldCheck className="text-green-400"/> Security Posture Upgrades</h2>
                    {securityPatches.length === 0 ? (
                        <div className="bg-[#111] border border-[#333] rounded-xl p-12 text-center text-gray-500">Run the pipeline first.</div>
                    ) : (
                        <div className="grid gap-4">
                            {securityPatches.map((patch, i) => (
                                <div key={i} className="bg-[#111] border border-green-500/30 rounded-lg p-5 flex items-start gap-4">
                                    <div className="bg-green-500/10 p-2 rounded-md"><ShieldCheck className="text-green-400 w-6 h-6" /></div>
                                    <div><h4 className="font-bold text-white mb-1">Vulnerability Remediated</h4><p className="text-gray-400 text-sm">{patch}</p></div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        )}
      </main>
    </div>
  );
}

export default App;
