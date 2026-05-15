import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, FileText, CheckCircle2, ArrowRight } from "lucide-react";
import ChatBubble from "../components/ChatBubble";
import ChatInput from "../components/ChatInput";
import LeadModal from "../components/LeadModal";
import { sendMessage, uploadFile } from "../api/api";

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [showLead, setShowLead] = useState(false);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isChatStarted, setIsChatStarted] = useState(false);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;
    const file = acceptedFiles[0];
    
    setUploading(true);
    try {
      await uploadFile(file);
      setUploadedFiles(prev => [...prev, file.name]);
    } catch (err) {
      alert("Upload failed: " + err.message);
    } finally {
      setUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    }
  });

  const send = async () => {
    if (!input.trim()) return;

    const currentInput = input;
    setInput(""); // Clear input immediately for better UX
    
    const userMsg = { role: "user", text: currentInput };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await sendMessage(currentInput);
      const botMsg = { role: "bot", text: res.answer, citations: res.citations };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [...prev, { role: "bot", text: "Sorry, an error occurred." }]);
    } finally {
      setLoading(false);
    }

    if (currentInput.toLowerCase().includes("interested") || currentInput.toLowerCase().includes("apply")) {
      setShowLead(true);
    }
  };

  return (
    <div className="flex-1 flex flex-col items-center px-6 py-8 relative">
      
      {!isChatStarted ? (
        <div className="w-full max-w-3xl mt-10 flex flex-col items-center animate-fade-in">
          <div className="bg-indigo-500/20 p-4 rounded-2xl mb-6">
            <FileText size={40} className="text-indigo-400" />
          </div>
          <h2 className="text-3xl font-bold text-white tracking-tight text-center mb-4">
            Upload Knowledge Base
          </h2>
          <p className="text-slate-400 text-center mb-10 max-w-lg">
            Upload any job description, engineering guideline, or benefits PDF before starting the chat.
          </p>

          {/* Drag & Drop Zone */}
          <div 
            {...getRootProps()} 
            className={`w-full p-10 border-2 border-dashed rounded-3xl transition-all cursor-pointer flex flex-col items-center justify-center text-center mb-6
              ${isDragActive ? 'border-indigo-400 bg-indigo-900/20' : 'border-white/10 hover:border-indigo-500/50 hover:bg-white/5 bg-slate-900/30'}`}
          >
            <input {...getInputProps()} />
            
            {uploading ? (
              <div className="flex flex-col items-center text-indigo-400">
                <div className="w-8 h-8 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mb-4"></div>
                <p className="font-medium">Uploading and Indexing...</p>
              </div>
            ) : (
              <>
                <UploadCloud size={32} className="text-slate-400 mb-4" />
                <p className="text-slate-200 font-medium mb-1">
                  {isDragActive ? "Drop the file here!" : "Drag & drop a file, or click to select"}
                </p>
                <p className="text-slate-500 text-sm">Supports PDF, DOCX, TXT (Max 5MB)</p>
              </>
            )}
          </div>

          {/* Uploaded Files Pills */}
          {uploadedFiles.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-8 justify-center">
              {uploadedFiles.map((file, i) => (
                <div key={i} className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-full text-xs font-medium">
                  <CheckCircle2 size={14} />
                  {file}
                </div>
              ))}
            </div>
          )}

          <button 
            onClick={() => setIsChatStarted(true)}
            className="mt-4 bg-white text-slate-900 hover:bg-slate-200 px-8 py-3.5 rounded-xl font-semibold transition flex items-center gap-2 shadow-xl shadow-white/10"
          >
            Start Chatting <ArrowRight size={18} />
          </button>
        </div>
      ) : (
        <>
          {/* Chat History */}
          <div className="w-full max-w-4xl flex flex-col flex-1 mb-24 overflow-y-auto pr-2 pb-10">
            {messages.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center text-slate-500 mt-20">
                <FileText size={48} className="mb-4 opacity-20" />
                <p>Chat session started. Ask a question below!</p>
              </div>
            ) : (
              messages.map((m, i) => (
                <ChatBubble key={i} role={m.role} text={m.text} citations={m.citations} />
              ))
            )}

            {loading && (
              <div className="flex w-full justify-start mb-6">
                <div className="flex items-center gap-2 glass px-5 py-3 rounded-2xl rounded-tl-none bg-slate-800/40">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Fixed Bottom Input */}
          <div className="fixed bottom-0 left-0 w-full bg-gradient-to-t from-[#09090b] via-[#09090b]/90 to-transparent pt-10 pb-8 px-6 pointer-events-none">
            <div className="pointer-events-auto flex flex-col items-center max-w-4xl mx-auto w-full">
              <ChatInput input={input} setInput={setInput} send={send} />
              {messages.length > 0 && (
                <div className="flex justify-center mt-4">
                  <button
                    onClick={() => setShowLead(true)}
                    className="text-xs text-emerald-400 hover:text-emerald-300 font-medium transition flex items-center gap-1"
                  >
                    I'm interested in applying
                  </button>
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {showLead && <LeadModal close={() => setShowLead(false)} />}
    </div>
  );
}
