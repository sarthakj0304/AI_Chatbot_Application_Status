import { SendHorizontal } from "lucide-react";

export default function ChatInput({ input, setInput, send }) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') send();
  };

  return (
    <div className="glass-panel p-2 flex gap-2 rounded-2xl border border-white/10 mx-auto w-full max-w-3xl shadow-2xl">
      <input
        className="flex-1 bg-transparent outline-none text-slate-200 px-4 py-3 placeholder:text-slate-500 font-medium"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask anything about the uploaded documents..."
      />
      <button
        onClick={send}
        disabled={!input.trim()}
        className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed px-5 py-3 rounded-xl transition flex items-center justify-center text-white"
      >
        <SendHorizontal size={20} />
      </button>
    </div>
  );
}
