import { useState, useEffect } from "react";
import { getLogs, getStats, getDocuments, uploadFile, getAnalytics } from "../api/api";
import StatsCard from "../components/StatsCard";
import { UploadCloud } from "lucide-react";

export default function AdminPage() {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState([]);
  const [docs, setDocs] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [uploading, setUploading] = useState(false);

  const fetchDocs = () => {
    getDocuments().then(setDocs).catch(console.error);
    getAnalytics().then(setAnalytics).catch(console.error);
  };

  useEffect(() => {
    getLogs().then(setLogs).catch(console.error);
    getStats().then(setStats).catch(console.error);
    fetchDocs();
    
    // Poll docs status every 5 seconds
    const interval = setInterval(fetchDocs, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setUploading(true);
    try {
      await uploadFile(file);
      fetchDocs();
    } catch (err) {
      alert("Upload failed: " + err.message);
    } finally {
      setUploading(false);
      e.target.value = ""; // Reset input
    }
  };

  return (
    <div className="flex-1 px-8 py-10 max-w-7xl mx-auto w-full animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-2xl font-bold text-white tracking-tight">System Dashboard</h2>
        <label className="bg-indigo-600 hover:bg-indigo-500 cursor-pointer px-5 py-2.5 rounded-xl transition flex items-center gap-2 text-sm font-medium text-white shadow-lg shadow-indigo-500/20">
          <UploadCloud size={18} />
          {uploading ? "Uploading..." : "Upload Document"}
          <input type="file" accept=".pdf,.docx,.txt" className="hidden" onChange={handleFileUpload} disabled={uploading} />
        </label>
      </div>

      {/* Top Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatsCard title="Total Conversations" value={logs.length} />
        <StatsCard title="Top Questions" value={stats.length} />
        <StatsCard title="Unanswered Queries" value={analytics?.unanswered_queries || 0} />
        <StatsCard title="Success Rate" value={`${analytics?.success_rate || 100}%`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Document Status */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-3xl">
          <h3 className="mb-6 text-white font-semibold flex items-center gap-2">
            Knowledge Base Index
          </h3>
          
          {docs.length === 0 ? (
            <div className="text-center py-10 text-slate-500">
              <UploadCloud size={32} className="mx-auto mb-3 opacity-50" />
              <p>No documents uploaded yet.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead>
                  <tr className="border-b border-white/10 text-slate-400">
                    <th className="py-3 px-4 font-medium">ID</th>
                    <th className="py-3 px-4 font-medium">Filename</th>
                    <th className="py-3 px-4 font-medium">Status</th>
                    <th className="py-3 px-4 font-medium">Uploaded At</th>
                  </tr>
                </thead>
                <tbody>
                  {docs.map((doc) => (
                    <tr key={doc.id} className="border-b border-white/5 hover:bg-white/5 transition-colors group">
                      <td className="py-3 px-4 text-slate-500">#{doc.id}</td>
                      <td className="py-3 px-4 text-slate-200 font-medium truncate max-w-[200px]">{doc.filename}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${
                          doc.status === 'completed' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                          doc.status === 'failed' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                          'bg-amber-500/10 text-amber-400 border-amber-500/20'
                        }`}>
                          {doc.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-500">{new Date(doc.upload_time).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Right Column */}
        <div className="space-y-8">
          {/* Most Asked Questions */}
          <div className="glass-panel p-6 rounded-3xl">
            <h3 className="mb-6 text-white font-semibold">Trending Queries</h3>
            {stats.length === 0 ? (
              <p className="text-sm text-slate-500 py-4 text-center">No queries tracked.</p>
            ) : (
              <div className="space-y-4">
                {stats.map((item, index) => (
                  <div key={index} className="flex justify-between items-start border-b border-white/5 pb-3 text-sm">
                    <span className="text-slate-300 pr-4">{item[0]}</span>
                    <span className="text-indigo-400 font-medium bg-indigo-500/10 px-2 py-0.5 rounded-md whitespace-nowrap">
                      {item[1]}x
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* Recent Logs Snippet */}
          <div className="glass-panel p-6 rounded-3xl max-h-[400px] overflow-y-auto">
            <h3 className="mb-6 text-white font-semibold sticky top-0 bg-[#161a29] z-10 py-2 -mt-2">Recent Logs</h3>
            {logs.length === 0 ? (
              <p className="text-sm text-slate-500 text-center">No conversations yet.</p>
            ) : (
              <div className="space-y-4">
                {logs.slice(0, 10).map((log, i) => (
                  <div key={i} className="bg-white/5 p-4 rounded-2xl text-sm">
                    <div className="text-indigo-300 font-medium mb-1">Q: {log[0]}</div>
                    <div className="text-slate-400 line-clamp-3">A: {log[1]}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
