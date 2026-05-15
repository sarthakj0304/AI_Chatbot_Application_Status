import { Link, useLocation } from "react-router-dom";
import { MessageSquare, Settings, Briefcase } from "lucide-react";

export default function Navbar() {
  const location = useLocation();

  return (
    <nav className="h-16 flex items-center justify-between px-6 border-b border-white/5 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
      <div className="flex items-center gap-3">
        <div className="bg-indigo-500/20 p-2 rounded-xl text-indigo-400">
          <Briefcase size={20} />
        </div>
        <h1 className="text-lg font-bold tracking-tight text-white">
          Career Context <span className="text-indigo-400">RAG</span>
        </h1>
      </div>

      <div className="flex items-center gap-2">
        <Link
          to="/"
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition ${
            location.pathname === "/"
              ? "bg-white/10 text-white"
              : "text-slate-400 hover:bg-white/5 hover:text-white"
          }`}
        >
          <MessageSquare size={16} />
          <span>Chat</span>
        </Link>
        <Link
          to="/admin"
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition ${
            location.pathname === "/admin"
              ? "bg-white/10 text-white"
              : "text-slate-400 hover:bg-white/5 hover:text-white"
          }`}
        >
          <Settings size={16} />
          <span>Admin</span>
        </Link>
      </div>
    </nav>
  );
}
