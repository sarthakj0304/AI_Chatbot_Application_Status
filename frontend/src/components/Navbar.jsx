import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="h-16 flex items-center justify-center relative glass">
      <Link
        to="/"
        className="absolute left-6 text-sm text-slate-400 hover:text-white"
      >
        Chat
      </Link>

      <h1 className="text-lg font-semibold tracking-wide">
        Vertex Labs Recruiting Assistant
      </h1>

      <Link
        to="/admin"
        className="absolute right-6 text-sm text-slate-400 hover:text-white"
      >
        Admin
      </Link>
    </nav>
  );
}
