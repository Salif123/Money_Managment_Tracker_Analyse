import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  LayoutDashboard, 
  UploadCloud, 
  Receipt, 
  CheckCircle2, 
  Server, 
  FolderGit2, 
  Cpu, 
  Database,
  RefreshCw,
  GitBranch,
  Laptop,
  Layers,
  ArrowUpRight
} from 'lucide-react'

export default function App() {
  const [activeTab, setActiveTab] = useState('Dashboard')
  const [backendStatus, setBackendStatus] = useState('checking') // 'checking', 'online', 'offline'
  const [loadingHealth, setLoadingHealth] = useState(false)

  const checkHealth = async () => {
    setLoadingHealth(true)
    try {
      // Calls relative URL path via Vite Proxy (vite.config.js proxy config maps this to http://localhost:8000/api/health)
      const response = await axios.get('/api/health')
      if (response.data && response.data.status === 'ok') {
        setBackendStatus('online')
      } else {
        setBackendStatus('offline')
      }
    } catch (error) {
      console.error("Health check failed:", error)
      setBackendStatus('offline')
    } finally {
      setLoadingHealth(false)
    }
  }

  useEffect(() => {
    checkHealth()
  }, [])

  const navItems = [
    { name: 'Dashboard', icon: LayoutDashboard },
    { name: 'Upload', icon: UploadCloud },
    { name: 'Transactions', icon: Receipt },
  ]

  const stats = [
    { name: 'Active Framework', value: 'React 18 + Vite', icon: Laptop, color: 'text-cyan-400', bg: 'bg-cyan-500/10' },
    { name: 'Backend Service', value: 'FastAPI', icon: Cpu, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
    { name: 'Database Storage', value: 'SQLite', icon: Database, color: 'text-amber-400', bg: 'bg-amber-500/10' },
    { name: 'CSS Engine', value: 'Tailwind CSS v3', icon: Layers, color: 'text-violet-400', bg: 'bg-violet-500/10' },
  ]

  return (
    <div className="flex h-full min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-indigo-600/30 selection:text-indigo-200">
      
      {/* SIDEBAR */}
      <aside className="w-64 flex-shrink-0 border-r border-slate-900 bg-slate-900/40 backdrop-blur-md flex flex-col justify-between p-6">
        <div>
          {/* Logo */}
          <div className="flex items-center space-x-3 mb-10 px-2">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Receipt className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-300">
                Bill Manager
              </h1>
              <span className="text-[10px] uppercase tracking-wider text-indigo-400 font-semibold font-mono">
                Local App v1.0
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = activeTab === item.name
              return (
                <button
                  key={item.name}
                  onClick={() => setActiveTab(item.name)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 group ${
                    isActive 
                      ? 'bg-gradient-to-r from-indigo-500/10 to-transparent text-indigo-400 border-l-2 border-indigo-500 font-medium'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                  }`}
                >
                  <Icon className={`h-5 w-5 transition-transform duration-300 group-hover:scale-110 ${
                    isActive ? 'text-indigo-400' : 'text-slate-400 group-hover:text-slate-300'
                  }`} />
                  <span className="text-sm">{item.name}</span>
                </button>
              )
            })}
          </nav>
        </div>

        {/* Footer info inside sidebar */}
        <div className="border-t border-slate-900/60 pt-6">
          <div className="flex items-center space-x-3">
            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs text-slate-500 font-medium">System Sandboxed</span>
          </div>
        </div>
      </aside>

      {/* MAIN WRAPPER */}
      <main className="flex-1 flex flex-col h-full min-h-screen overflow-y-auto">
        
        {/* HEADER */}
        <header className="h-20 border-b border-slate-900/60 flex items-center justify-between px-10 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-slate-400 font-medium capitalize">Workspace:</span>
            <span className="text-sm font-mono bg-slate-900 px-2 py-1 rounded border border-slate-800 text-indigo-300 text-xs">
              d:/MONEY TRACKER/bill-manager
            </span>
          </div>

          {/* Connection Status Checker */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 bg-slate-900 px-3 py-1.5 rounded-full border border-slate-800">
              <Server className="h-4 w-4 text-slate-400" />
              <span className="text-xs text-slate-300 font-medium">Backend:</span>
              
              {backendStatus === 'checking' && (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-400">
                  Checking...
                </span>
              )}
              {backendStatus === 'online' && (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Online
                </span>
              )}
              {backendStatus === 'offline' && (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20 animate-pulse">
                  Offline
                </span>
              )}
            </div>

            <button 
              onClick={checkHealth}
              disabled={loadingHealth}
              className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-850 hover:text-white transition-all duration-200 text-slate-400 disabled:opacity-50"
              title="Refresh connection status"
            >
              <RefreshCw className={`h-4 w-4 ${loadingHealth ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </header>

        {/* CONTENT BODY */}
        <section className="flex-1 p-10 max-w-6xl mx-auto w-full space-y-10">
          
          {/* Welcome Dashboard Banner */}
          <div className="relative overflow-hidden rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-indigo-950/40 via-slate-900/60 to-slate-950 p-8 shadow-2xl">
            {/* Glowing background circles */}
            <div className="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-indigo-500/10 blur-3xl pointer-events-none" />
            <div className="absolute -left-20 -bottom-20 h-40 w-40 rounded-full bg-violet-600/10 blur-3xl pointer-events-none" />
            
            <div className="relative z-10 space-y-4">
              <div className="inline-flex items-center space-x-2 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-3 py-1 rounded-full text-xs font-semibold">
                <CheckCircle2 className="h-4 w-4 mr-0.5" />
                Scaffolding Complete
              </div>

              <h2 className="text-4xl font-extrabold tracking-tight text-white font-mono">
                Bill Manager — Section 1 complete
              </h2>

              <p className="text-slate-300 max-w-2xl text-base leading-relaxed">
                We've successfully set up the development environment, package managers, and directories. 
                The Vite development server is proxying requests seamlessly to our FastAPI service. 
                Below is the project scaffold overview and initial connection diagnostics.
              </p>

              <div className="pt-4 flex items-center space-x-4">
                <a 
                  href="http://localhost:8000/api/health" 
                  target="_blank" 
                  rel="noreferrer" 
                  className="inline-flex items-center space-x-2 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors bg-slate-900 border border-slate-800 px-4 py-2.5 rounded-xl"
                >
                  <span>Verify raw JSON health check</span>
                  <ArrowUpRight className="h-3.5 w-3.5" />
                </a>
              </div>
            </div>
          </div>

          {/* Section: Status Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {stats.map((stat, idx) => {
              const Icon = stat.icon
              return (
                <div key={idx} className="bg-slate-900/30 backdrop-blur-sm border border-slate-900 p-5 rounded-2xl flex items-center space-x-4 hover:border-slate-800 transition-all duration-300">
                  <div className={`p-3 rounded-xl ${stat.bg} ${stat.color}`}>
                    <Icon className="h-6 w-6" />
                  </div>
                  <div>
                    <span className="block text-[11px] uppercase tracking-wider text-slate-500 font-semibold">{stat.name}</span>
                    <span className="block text-base font-bold text-white mt-0.5">{stat.value}</span>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Scaffold Status Details */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-2">
            
            {/* Left side details */}
            <div className="md:col-span-2 space-y-6">
              <h3 className="text-xl font-bold tracking-tight text-white flex items-center space-x-2">
                <FolderGit2 className="h-5 w-5 text-indigo-400" />
                <span>Files Created & Tracked</span>
              </h3>

              <div className="border border-slate-900 rounded-2xl overflow-hidden bg-slate-900/10">
                <table className="min-w-full divide-y divide-slate-900/80">
                  <thead>
                    <tr className="bg-slate-900/40 text-[10px] uppercase font-bold tracking-wider text-slate-400">
                      <th className="px-6 py-3.5 text-left">Location</th>
                      <th className="px-6 py-3.5 text-left">Purpose</th>
                      <th className="px-6 py-3.5 text-right">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-900/50 text-xs font-mono text-slate-300">
                    <tr>
                      <td className="px-6 py-4 text-white font-medium">backend/main.py</td>
                      <td className="px-6 py-4 font-sans text-slate-400">FastAPI application loader & CORS rules</td>
                      <td className="px-6 py-4 text-right text-emerald-400">Created</td>
                    </tr>
                    <tr>
                      <td className="px-6 py-4 text-white font-medium">backend/config.py</td>
                      <td className="px-6 py-4 font-sans text-slate-400">App configuration settings via env vars</td>
                      <td className="px-6 py-4 text-right text-emerald-400">Created</td>
                    </tr>
                    <tr>
                      <td className="px-6 py-4 text-white font-medium">backend/routers/health.py</td>
                      <td className="px-6 py-4 font-sans text-slate-400">Health endpoint router mapping</td>
                      <td className="px-6 py-4 text-right text-emerald-400">Created</td>
                    </tr>
                    <tr>
                      <td className="px-6 py-4 text-white font-medium">frontend/vite.config.js</td>
                      <td className="px-6 py-4 font-sans text-slate-400">Vite config and server-side API proxying</td>
                      <td className="px-6 py-4 text-right text-emerald-400">Created</td>
                    </tr>
                    <tr>
                      <td className="px-6 py-4 text-white font-medium">frontend/src/App.jsx</td>
                      <td className="px-6 py-4 font-sans text-slate-400">Application shell & dashboard wrapper</td>
                      <td className="px-6 py-4 text-right text-emerald-400">Created</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Right side connection info */}
            <div className="bg-gradient-to-b from-slate-900/40 to-slate-950 border border-slate-900 p-6 rounded-2xl flex flex-col justify-between">
              <div>
                <h4 className="font-bold text-white text-base mb-3 flex items-center space-x-2">
                  <GitBranch className="h-4.5 w-4.5 text-indigo-400" />
                  <span>Dev Environment Rules</span>
                </h4>
                <p className="text-xs text-slate-400 leading-relaxed mb-4">
                  The frontend uses Vite as a development server proxying all <strong>/api</strong> requests to localhost:8000. 
                  This solves local CORS issues and maps static uploads smoothly under the <strong>/uploads</strong> path.
                </p>
                <div className="space-y-3">
                  <div className="bg-slate-900 border border-slate-800/80 rounded-lg p-3 text-xs">
                    <span className="block text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-1">API Proxy Endpoint</span>
                    <span className="font-mono text-indigo-300">/api/health</span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">Proxied to → http://localhost:8000/api/health</span>
                  </div>
                  <div className="bg-slate-900 border border-slate-800/80 rounded-lg p-3 text-xs">
                    <span className="block text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-1">Static Asset Path</span>
                    <span className="font-mono text-indigo-300">/uploads/</span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">Mapped to → ../uploads directory</span>
                  </div>
                </div>
              </div>

              <div className="mt-6 border-t border-slate-900/60 pt-4 flex items-center justify-between text-xs text-slate-500 font-mono">
                <span>PORT: 5173 (React)</span>
                <span>PORT: 8000 (FastAPI)</span>
              </div>
            </div>

          </div>

        </section>

      </main>

    </div>
  )
}
