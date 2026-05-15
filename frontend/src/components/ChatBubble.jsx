import { Bot, User } from "lucide-react";

export default function ChatBubble({ role, text, citations = [] }) {
  const isUser = role === "user";
  
  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"} mb-6`}>
      <div className={`flex max-w-[85%] sm:max-w-[75%] gap-4 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
        
        {/* Avatar */}
        <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center shadow-lg border border-white/10 ${
          isUser ? "bg-indigo-600 text-white" : "bg-emerald-600 text-white"
        }`}>
          {isUser ? <User size={20} /> : <Bot size={20} />}
        </div>
        
        {/* Message Content */}
        <div className={`glass px-5 py-4 rounded-2xl text-sm leading-relaxed ${
          isUser ? "bg-indigo-900/30 rounded-tr-none" : "bg-slate-800/40 rounded-tl-none"
        }`}>
          <div className="whitespace-pre-wrap text-slate-200">{text}</div>
          
          {citations && citations.length > 0 && (
            <div className="mt-4 pt-4 border-t border-white/10">
              <p className="text-xs text-slate-400 font-semibold mb-3 flex items-center gap-2">
                <span className="w-1 h-1 rounded-full bg-emerald-400 animate-pulse"></span>
                Retrieved Sources
              </p>
              <div className="flex flex-col gap-2">
                {citations.map((cite, i) => (
                  <div key={i} className="bg-slate-900/50 rounded-lg p-3 text-xs text-slate-300 border border-white/5 hover:bg-slate-800/50 transition-colors">
                    <span className="text-indigo-400 font-medium inline-block mb-1">{cite.filename}</span>
                    <p className="opacity-80 italic line-clamp-3">"{cite.text_snippet}"</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
