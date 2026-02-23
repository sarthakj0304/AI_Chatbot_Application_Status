import { useState, useEffect } from "react";
import { getLogs, getStats } from "../api/api";
import StatsCard from "../components/StatsCard";

export default function AdminPage() {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState([]);

  useEffect(() => {
    getLogs().then(setLogs);
    getStats().then(setStats);
  }, []);

  return (
    <div className="flex-1 px-8 py-10 max-w-6xl mx-auto">
      <h2 className="text-xl font-semibold mb-8">Admin Dashboard</h2>

      {/* Top Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
        <StatsCard title="Total Conversations" value={logs.length} />
        <StatsCard title="Top Questions Tracked" value={stats.length} />
      </div>

      {/* Most Asked Questions */}
      <div className="glass p-6 rounded-2xl mb-10">
        <h3 className="mb-4 text-slate-400 text-lg">Most Asked Questions</h3>

        {stats.length === 0 && (
          <p className="text-sm text-slate-500">No questions asked yet.</p>
        )}

        {stats.map((item, index) => (
          <div
            key={index}
            className="flex justify-between border-b border-white/10 py-3 text-sm"
          >
            <span className="text-slate-200">{item[0]}</span>
            <span className="text-indigo-400 font-medium">{item[1]} times</span>
          </div>
        ))}
      </div>

      {/* Conversation Logs */}
      <div className="glass p-6 rounded-2xl max-h-[400px] overflow-y-auto">
        <h3 className="mb-4 text-slate-400 text-lg">Conversation Logs</h3>

        {logs.length === 0 && (
          <p className="text-sm text-slate-500">No conversations yet.</p>
        )}

        {logs.map((log, i) => (
          <div key={i} className="border-b border-white/10 py-3 text-sm">
            <div className="text-indigo-400">Q: {log[0]}</div>
            <div className="text-slate-300 mt-1">A: {log[1]}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
